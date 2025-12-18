"""
S39 - Shard Migration Manager

Handles migration from single database to sharded architecture:
- Shadow mode (dual-write)
- Data validation
- Cutover
- Rollback
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from app.data.sharding.router import Domain, ShardRouter, router

logger = logging.getLogger(__name__)

# Valid SQL identifier pattern (prevents SQL injection)
_IDENTIFIER_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')


def _validate_identifier(name: str, kind: str = "identifier") -> None:
    """
    Validate that a string is a safe SQL identifier.

    Args:
        name: The identifier to validate
        kind: Description for error message (e.g., "table", "column")

    Raises:
        ValueError: If identifier is invalid
    """
    if not name or not _IDENTIFIER_PATTERN.match(name):
        raise ValueError(f"Invalid {kind} name: {name!r}")


class MigrationPhase(str, Enum):
    """Migration phases."""

    DISABLED = "disabled"         # Sharding not active
    SHADOW_MODE = "shadow_mode"   # Dual-write to both old and new
    VALIDATION = "validation"     # Validating data consistency
    CUTOVER = "cutover"           # Reading from new, writing to new
    CLEANUP = "cleanup"           # Old writes disabled
    COMPLETE = "complete"         # Migration finished


@dataclass
class MigrationConfig:
    """Configuration for migration process."""

    phase: MigrationPhase = MigrationPhase.DISABLED
    shadow_mode_duration_hours: int = 48
    validation_sample_rate: float = 0.1  # Validate 10% of writes
    batch_size: int = 1000
    enable_rollback: bool = True
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class MigrationStats:
    """Statistics for migration progress."""

    phase: MigrationPhase
    records_migrated: int = 0
    records_validated: int = 0
    records_failed: int = 0
    validation_errors: List[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    started_at: Optional[datetime] = None
    last_updated: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase.value,
            "records_migrated": self.records_migrated,
            "records_validated": self.records_validated,
            "records_failed": self.records_failed,
            "validation_errors": self.validation_errors[:10],  # Limit errors
            "error_count": len(self.validation_errors),
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }


@dataclass
class WriteResult:
    """Result of a write operation."""

    success: bool
    legacy_success: bool
    shard_success: bool
    shard_domain: Optional[Domain] = None
    error: Optional[str] = None
    validation_mismatch: bool = False


class ShadowModeWriter:
    """
    Writer that supports shadow mode (dual-write).

    In shadow mode, writes go to both the legacy database
    and the appropriate shard. Validation ensures consistency.
    """

    def __init__(
        self,
        shard_router: ShardRouter,
        legacy_pool: Any,  # asyncpg.Pool
        config: Optional[MigrationConfig] = None,
    ):
        self.router = shard_router
        self.legacy_pool = legacy_pool
        self.config = config or MigrationConfig()
        self._stats = MigrationStats(phase=self.config.phase)
        self._validators: Dict[str, Callable] = {}

    @property
    def phase(self) -> MigrationPhase:
        """Current migration phase."""
        return self.config.phase

    @property
    def stats(self) -> MigrationStats:
        """Get current migration stats."""
        return self._stats

    def set_phase(self, phase: MigrationPhase) -> None:
        """Update migration phase."""
        old_phase = self.config.phase
        self.config.phase = phase
        self._stats.phase = phase
        logger.info(f"Migration phase changed: {old_phase.value} -> {phase.value}")

        if phase == MigrationPhase.SHADOW_MODE and not self.config.started_at:
            self.config.started_at = datetime.now(timezone.utc)
            self._stats.started_at = self.config.started_at

    def register_validator(
        self,
        table: str,
        validator: Callable[[Dict, Dict], bool],
    ) -> None:
        """
        Register a validator for a table.

        Args:
            table: Table name
            validator: Function that takes (legacy_row, shard_row) and returns True if equal
        """
        self._validators[table] = validator

    async def write(
        self,
        table: str,
        data: Dict[str, Any],
        claim_text: Optional[str] = None,
        explicit_domain: Optional[Domain] = None,
    ) -> WriteResult:
        """
        Write data with shadow mode support.

        Args:
            table: Table name (must be a valid SQL identifier)
            data: Data to insert (keys must be valid SQL identifiers)
            claim_text: Text for domain routing (optional)
            explicit_domain: Override domain (optional)

        Returns:
            WriteResult with success status

        Raises:
            ValueError: If table or column names are invalid
        """
        # Validate identifiers to prevent SQL injection
        _validate_identifier(table, "table")
        for col in data.keys():
            _validate_identifier(col, "column")

        # Determine target domain
        if explicit_domain:
            domain = explicit_domain
        elif claim_text:
            domain = self.router.route(claim_text)
        else:
            domain = Domain.DEFAULT

        # Build INSERT query
        columns = list(data.keys())
        placeholders = [f"${i + 1}" for i in range(len(columns))]
        values = list(data.values())

        insert_query = f"""
            INSERT INTO {table} ({', '.join(columns)})
            VALUES ({', '.join(placeholders)})
            RETURNING *
        """

        result = WriteResult(
            success=False,
            legacy_success=False,
            shard_success=False,
            shard_domain=domain,
        )

        try:
            if self.config.phase == MigrationPhase.DISABLED:
                # Only write to legacy
                async with self.legacy_pool.acquire() as conn:
                    await conn.execute(insert_query, *values)
                result.legacy_success = True
                result.success = True

            elif self.config.phase == MigrationPhase.SHADOW_MODE:
                # Dual-write to both
                legacy_result, shard_result = await asyncio.gather(
                    self._write_legacy(insert_query, values),
                    self._write_shard(domain, insert_query, values),
                    return_exceptions=True,
                )

                result.legacy_success = not isinstance(legacy_result, Exception)
                result.shard_success = not isinstance(shard_result, Exception)
                result.success = result.legacy_success  # Legacy is source of truth

                if not result.legacy_success:
                    result.error = str(legacy_result)
                elif not result.shard_success:
                    logger.warning(f"Shadow write to shard failed: {shard_result}")

                self._stats.records_migrated += 1

            elif self.config.phase in (MigrationPhase.CUTOVER, MigrationPhase.COMPLETE):
                # Only write to shard
                async with self.router.get_connection(domain) as conn:
                    await conn.execute(insert_query, *values)
                result.shard_success = True
                result.success = True

        except Exception as e:
            result.error = str(e)
            self._stats.records_failed += 1
            logger.error(f"Write failed: {e}")

        self._stats.last_updated = datetime.now(timezone.utc)
        return result

    async def _write_legacy(self, query: str, values: list) -> Dict:
        """Write to legacy database."""
        async with self.legacy_pool.acquire() as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else {}

    async def _write_shard(self, domain: Domain, query: str, values: list) -> Dict:
        """Write to shard."""
        async with self.router.get_connection(domain) as conn:
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else {}

    async def validate_consistency(
        self,
        table: str,
        id_column: str,
        sample_size: int = 1000,
    ) -> Tuple[int, int, List[str]]:
        """
        Validate data consistency between legacy and shards.

        Args:
            table: Table name (must be a valid SQL identifier)
            id_column: ID column name (must be a valid SQL identifier)
            sample_size: Number of records to validate

        Returns:
            Tuple of (validated_count, mismatch_count, error_messages)

        Raises:
            ValueError: If table or column name is invalid
        """
        # Validate identifiers to prevent SQL injection
        _validate_identifier(table, "table")
        _validate_identifier(id_column, "column")

        validated = 0
        mismatches = 0
        errors = []

        # Get sample from legacy
        async with self.legacy_pool.acquire() as conn:
            legacy_rows = await conn.fetch(
                f"SELECT * FROM {table} ORDER BY RANDOM() LIMIT $1",
                sample_size,
            )

        for legacy_row in legacy_rows:
            legacy_dict = dict(legacy_row)
            record_id = legacy_dict.get(id_column)

            # Try to find in each shard
            found = False
            for domain in Domain:
                try:
                    async with self.router.get_connection(domain) as conn:
                        shard_row = await conn.fetchrow(
                            f"SELECT * FROM {table} WHERE {id_column} = $1",
                            record_id,
                        )
                        if shard_row:
                            found = True
                            shard_dict = dict(shard_row)

                            # Validate with custom validator or default
                            validator = self._validators.get(
                                table, self._default_validator
                            )
                            if not validator(legacy_dict, shard_dict):
                                mismatches += 1
                                errors.append(
                                    f"Mismatch for {id_column}={record_id} in {domain.value}"
                                )
                            break
                except Exception as e:
                    logger.error(f"Validation error for {record_id}: {e}")

            if not found:
                mismatches += 1
                errors.append(f"Record {id_column}={record_id} not found in any shard")

            validated += 1

        self._stats.records_validated = validated
        self._stats.validation_errors.extend(errors)

        return validated, mismatches, errors

    def _default_validator(
        self,
        legacy: Dict[str, Any],
        shard: Dict[str, Any],
    ) -> bool:
        """Default validator - compare all fields."""
        # Ignore internal fields
        ignore_fields = {"_shard", "created_at", "updated_at"}

        for key in legacy:
            if key in ignore_fields:
                continue
            if key not in shard:
                return False
            if legacy[key] != shard[key]:
                return False

        return True


class MigrationManager:
    """
    Manages the complete migration process.

    Phases:
    1. DISABLED: Normal operation, single database
    2. SHADOW_MODE: Dual-write to legacy and shards
    3. VALIDATION: Validate data consistency
    4. CUTOVER: Switch reads to shards
    5. CLEANUP: Disable legacy writes
    6. COMPLETE: Migration finished
    """

    def __init__(
        self,
        shard_router: ShardRouter,
        legacy_pool: Any,
        config: Optional[MigrationConfig] = None,
    ):
        self.router = shard_router
        self.legacy_pool = legacy_pool
        self.config = config or MigrationConfig()
        self.writer = ShadowModeWriter(shard_router, legacy_pool, self.config)
        self._migration_tasks: List[asyncio.Task] = []

    async def start_shadow_mode(self) -> None:
        """Start shadow mode (dual-write)."""
        logger.info("Starting shadow mode migration")
        self.writer.set_phase(MigrationPhase.SHADOW_MODE)

    async def start_validation(
        self,
        tables: List[str],
        id_columns: Dict[str, str],
        sample_size: int = 1000,
    ) -> Dict[str, Tuple[int, int, List[str]]]:
        """
        Start validation phase.

        Args:
            tables: List of tables to validate
            id_columns: Mapping of table name to ID column name
            sample_size: Number of records to validate per table

        Returns:
            Dict mapping table name to validation results
        """
        logger.info("Starting validation phase")
        self.writer.set_phase(MigrationPhase.VALIDATION)

        results = {}
        for table in tables:
            id_col = id_columns.get(table, "id")
            validated, mismatches, errors = await self.writer.validate_consistency(
                table, id_col, sample_size
            )
            results[table] = (validated, mismatches, errors)
            logger.info(
                f"Validated {table}: {validated} records, {mismatches} mismatches"
            )

        return results

    async def execute_cutover(self) -> None:
        """Execute cutover to shards."""
        logger.info("Executing cutover to shards")

        # Validate before cutover
        if self.writer.stats.records_failed > 0:
            raise RuntimeError(
                f"Cannot cutover with {self.writer.stats.records_failed} failed records"
            )

        self.writer.set_phase(MigrationPhase.CUTOVER)
        logger.info("Cutover complete - now reading from shards")

    async def rollback(self) -> None:
        """Rollback to legacy database."""
        if not self.config.enable_rollback:
            raise RuntimeError("Rollback is disabled")

        logger.warning("Rolling back migration to legacy database")
        self.writer.set_phase(MigrationPhase.DISABLED)

    async def complete_migration(self) -> None:
        """Mark migration as complete."""
        logger.info("Completing migration")
        self.writer.set_phase(MigrationPhase.COMPLETE)
        self.config.completed_at = datetime.now(timezone.utc)

    async def migrate_batch(
        self,
        table: str,
        query: str,
        batch_size: int = 1000,
        id_column: str = "id",
        domain_column: Optional[str] = None,
        text_column: Optional[str] = None,
    ) -> int:
        """
        Migrate a batch of records from legacy to shards.

        Args:
            table: Target table (must be a valid SQL identifier)
            query: SELECT query to get records from legacy
            batch_size: Number of records per batch
            id_column: ID column name (must be a valid SQL identifier)
            domain_column: Column containing domain (optional, must be valid)
            text_column: Column containing text for routing (optional, must be valid)

        Returns:
            Number of records migrated

        Raises:
            ValueError: If table or column names are invalid
        """
        # Validate identifiers to prevent SQL injection
        _validate_identifier(table, "table")
        _validate_identifier(id_column, "column")
        if domain_column:
            _validate_identifier(domain_column, "column")
        if text_column:
            _validate_identifier(text_column, "column")

        total_migrated = 0

        async with self.legacy_pool.acquire() as conn:
            # Get total count
            count_query = f"SELECT COUNT(*) FROM ({query}) AS subq"
            total = await conn.fetchval(count_query)
            logger.info(f"Migrating {total} records from {table}")

            # Process in batches using keyset pagination (more efficient than OFFSET)
            last_cursor: Optional[Any] = None
            while True:
                # Build query with keyset cursor for efficient pagination
                if last_cursor is not None:
                    batch_query = (
                        f"SELECT * FROM ({query}) AS subq "
                        f"WHERE {id_column} > $1 "
                        f"ORDER BY {id_column} LIMIT {batch_size}"
                    )
                    rows = await conn.fetch(batch_query, last_cursor)
                else:
                    batch_query = (
                        f"SELECT * FROM ({query}) AS subq "
                        f"ORDER BY {id_column} LIMIT {batch_size}"
                    )
                    rows = await conn.fetch(batch_query)

                if not rows:
                    break

                for row in rows:
                    row_dict = dict(row)
                    record_id = row_dict.get(id_column)

                    # Determine domain
                    if domain_column and row_dict.get(domain_column):
                        try:
                            domain = Domain(row_dict[domain_column])
                        except ValueError:
                            domain = Domain.DEFAULT
                    elif text_column and row_dict.get(text_column):
                        domain = self.router.route(row_dict[text_column])
                    else:
                        domain = Domain.DEFAULT

                    # Insert into shard
                    try:
                        async with self.router.get_connection(domain) as shard_conn:
                            columns = list(row_dict.keys())
                            placeholders = [f"${i + 1}" for i in range(len(columns))]
                            values = list(row_dict.values())

                            await shard_conn.execute(
                                f"""
                                INSERT INTO {table} ({', '.join(columns)})
                                VALUES ({', '.join(placeholders)})
                                ON CONFLICT ({id_column}) DO NOTHING
                                """,
                                *values,
                            )
                            total_migrated += 1
                    except Exception as e:
                        logger.error(f"Failed to migrate record {record_id}: {e}")
                        self.writer.stats.records_failed += 1

                # Update cursor for keyset pagination (rows guaranteed non-empty here)
                last_cursor = rows[-1][id_column]

                logger.info(f"Migrated {total_migrated}/{total} records")

                # Exit if we got fewer rows than batch_size (last batch)
                if len(rows) < batch_size:
                    break

        self.writer.stats.records_migrated = total_migrated
        return total_migrated

    def get_status(self) -> Dict[str, Any]:
        """Get current migration status."""
        return {
            "phase": self.config.phase.value,
            "config": {
                "shadow_mode_duration_hours": self.config.shadow_mode_duration_hours,
                "batch_size": self.config.batch_size,
                "enable_rollback": self.config.enable_rollback,
            },
            "stats": self.writer.stats.to_dict(),
            "started_at": self.config.started_at.isoformat() if self.config.started_at else None,
            "completed_at": self.config.completed_at.isoformat() if self.config.completed_at else None,
        }
