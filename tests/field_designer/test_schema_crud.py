from __future__ import annotations
from pathlib import Path

import pytest

from inspectah.fields.designer import (
    FieldDefinition,
    ComputedFieldDefinition,
    create_schema,
    update_schema,
    list_schemas,
    load_schema,
)


def _make_fields() -> list[FieldDefinition]:
    return [
        FieldDefinition(name="title", type="text", path="item.title"),
        FieldDefinition(name="url", type="text", path="item.link", transforms=["normalize_url"]),
        FieldDefinition(name="published_at", type="timestamp", path="item.published", transforms=["parse_rfc822_date"]),
    ]


def _make_computed() -> list[ComputedFieldDefinition]:
    return [
        ComputedFieldDefinition(name="title_len", type="number", expression="length(title)", fallback=0),
        ComputedFieldDefinition(name="is_recent", type="bool", expression="if(published_at is not None, True, False)", fallback=False),
    ]


def test_create_and_update_schema(tmp_path: Path) -> None:
    fields = _make_fields()
    computed = _make_computed()

    schema = create_schema(
        "news_core",
        fields,
        computed_fields=computed,
        status="draft",
        description="Schema inicial",
        owner="leslie",
        registry_dir=tmp_path,
    )

    assert schema.version == 1
    schema_file = tmp_path / "schemas" / "news_core" / "v1.yaml"
    assert schema_file.exists()

    schema_v2 = update_schema(
        "news_core",
        fields,
        computed_fields=computed,
        status="active",
        description="Schema ativo",
        owner="leslie",
        registry_dir=tmp_path,
    )

    assert schema_v2.version == 2
    assert schema_v2.status == "active"

    listed = list_schemas(registry_dir=tmp_path)
    assert len(listed) == 1
    assert listed[0].version == 2
    assert listed[0].status == "active"

    loaded_v1 = load_schema("news_core", version=1, registry_dir=tmp_path)
    assert loaded_v1.version == 1
    assert len(loaded_v1.fields) == len(fields)
    assert len(loaded_v1.computed_fields) == len(computed)

    loaded_latest = load_schema("news_core", registry_dir=tmp_path)
    assert loaded_latest.version == 2
