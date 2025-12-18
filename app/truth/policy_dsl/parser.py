"""
Truth Policy DSL Parser — S37

Parses policy text into an AST.
"""

from __future__ import annotations

import re
from typing import Any, List, Optional, Tuple, Union

from app.truth.policy_dsl.grammar import (
    KNOWN_ACTIONS,
    KNOWN_CONDITIONS,
    KNOWN_FIELDS,
    KNOWN_MODIFIERS,
    OnThenRule,
    PolicyAST,
    RequireCondition,
    Token,
    TokenType,
)


class PolicyParseError(Exception):
    """Error during policy parsing."""

    def __init__(self, message: str, line: int = 0, column: int = 0):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Line {line}, Col {column}: {message}")


class PolicyLexer:
    """
    Lexer for the Policy DSL.

    Tokenizes policy text into a stream of tokens.
    """

    KEYWORDS = {
        "POLICY": TokenType.POLICY,
        "DOMAIN": TokenType.DOMAIN,
        "GATE": TokenType.GATE,
        "REQUIRE": TokenType.REQUIRE,
        "ON": TokenType.ON,
        "THEN": TokenType.THEN,
        "VERSION": TokenType.VERSION,
        "AND": TokenType.AND,
        "OR": TokenType.OR,
        "NOT": TokenType.NOT,
    }

    OPERATORS = {
        ">=": TokenType.GTE,
        "<=": TokenType.LTE,
        ">": TokenType.GT,
        "<": TokenType.LT,
        "=": TokenType.EQ,
        "!=": TokenType.NEQ,
    }

    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Tokenize the input text."""
        while self.pos < len(self.text):
            self._skip_whitespace_and_comments()
            if self.pos >= len(self.text):
                break

            char = self.text[self.pos]

            # Check for operators (two-char first)
            two_char = self.text[self.pos : self.pos + 2]
            if two_char in self.OPERATORS:
                self.tokens.append(
                    Token(self.OPERATORS[two_char], two_char, self.line, self.column)
                )
                self._advance(2)
                continue

            if char in self.OPERATORS:
                self.tokens.append(
                    Token(self.OPERATORS[char], char, self.line, self.column)
                )
                self._advance()
                continue

            # Symbols
            if char == "{":
                self.tokens.append(Token(TokenType.LBRACE, char, self.line, self.column))
                self._advance()
                continue
            if char == "}":
                self.tokens.append(Token(TokenType.RBRACE, char, self.line, self.column))
                self._advance()
                continue
            if char == "(":
                self.tokens.append(Token(TokenType.LPAREN, char, self.line, self.column))
                self._advance()
                continue
            if char == ")":
                self.tokens.append(Token(TokenType.RPAREN, char, self.line, self.column))
                self._advance()
                continue
            if char == ";":
                self.tokens.append(
                    Token(TokenType.SEMICOLON, char, self.line, self.column)
                )
                self._advance()
                continue
            if char == ",":
                self.tokens.append(Token(TokenType.COMMA, char, self.line, self.column))
                self._advance()
                continue

            # Strings
            if char == '"' or char == "'":
                self._read_string(char)
                continue

            # Numbers
            if char.isdigit() or (char == "." and self._peek().isdigit()):
                self._read_number()
                continue

            # Identifiers and keywords
            if char.isalpha() or char == "_":
                self._read_identifier()
                continue

            # Newlines
            if char == "\n":
                self.tokens.append(
                    Token(TokenType.NEWLINE, char, self.line, self.column)
                )
                self.line += 1
                self.column = 1
                self.pos += 1
                continue

            raise PolicyParseError(
                f"Unexpected character: {char}", self.line, self.column
            )

        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens

    def _advance(self, count: int = 1) -> None:
        """Advance position by count."""
        self.pos += count
        self.column += count

    def _peek(self) -> str:
        """Peek at next character."""
        if self.pos + 1 < len(self.text):
            return self.text[self.pos + 1]
        return ""

    def _skip_whitespace_and_comments(self) -> None:
        """Skip whitespace and comments."""
        while self.pos < len(self.text):
            char = self.text[self.pos]

            # Skip spaces and tabs
            if char in " \t\r":
                self._advance()
                continue

            # Skip comments (# to end of line)
            if char == "#":
                while self.pos < len(self.text) and self.text[self.pos] != "\n":
                    self.pos += 1
                continue

            break

    def _read_string(self, quote: str) -> None:
        """Read a string literal."""
        start_line = self.line
        start_col = self.column
        self._advance()  # Skip opening quote
        value = ""
        while self.pos < len(self.text) and self.text[self.pos] != quote:
            if self.text[self.pos] == "\\":
                self._advance()
                if self.pos < len(self.text):
                    value += self.text[self.pos]
                    self._advance()
            else:
                value += self.text[self.pos]
                self._advance()
        if self.pos >= len(self.text):
            raise PolicyParseError("Unterminated string", start_line, start_col)
        self._advance()  # Skip closing quote
        self.tokens.append(Token(TokenType.STRING, value, start_line, start_col))

    def _read_number(self) -> None:
        """Read a number literal."""
        start_col = self.column
        value = ""
        has_dot = False
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isdigit():
                value += char
                self._advance()
            elif char == "." and not has_dot:
                value += char
                has_dot = True
                self._advance()
            else:
                break
        num_value: Union[int, float] = float(value) if has_dot else int(value)
        self.tokens.append(Token(TokenType.NUMBER, num_value, self.line, start_col))

    def _read_identifier(self) -> None:
        """Read an identifier or keyword."""
        start_col = self.column
        value = ""
        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isalnum() or char == "_":
                value += char
                self._advance()
            else:
                break
        # Check if keyword
        upper_value = value.upper()
        if upper_value in self.KEYWORDS:
            self.tokens.append(
                Token(self.KEYWORDS[upper_value], value, self.line, start_col)
            )
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, value, self.line, start_col))


class PolicyParser:
    """
    Parser for the Policy DSL.

    Parses tokens into a PolicyAST.
    """

    def __init__(self):
        self.tokens: List[Token] = []
        self.pos = 0

    def parse(self, text: str) -> PolicyAST:
        """
        Parse policy text into an AST.

        Args:
            text: Policy DSL text

        Returns:
            PolicyAST

        Raises:
            PolicyParseError: If parsing fails
        """
        lexer = PolicyLexer(text)
        self.tokens = lexer.tokenize()
        self.pos = 0

        # Parse policy structure
        name = self._parse_policy_declaration()
        domain = self._parse_domain()
        gate = self._parse_gate()
        requirements = self._parse_requirements()
        rules = self._parse_rules()
        version = self._parse_version()

        return PolicyAST(
            name=name,
            domain=domain,
            gate=gate,
            requirements=requirements,
            rules=rules,
            version=version,
        )

    def _current(self) -> Token:
        """Get current token."""
        if self.pos >= len(self.tokens):
            return Token(TokenType.EOF, None, 0, 0)
        return self.tokens[self.pos]

    def _peek(self, offset: int = 1) -> Token:
        """Peek at future token."""
        pos = self.pos + offset
        if pos >= len(self.tokens):
            return Token(TokenType.EOF, None, 0, 0)
        return self.tokens[pos]

    def _advance(self) -> Token:
        """Advance and return current token."""
        token = self._current()
        self.pos += 1
        return token

    def _skip_newlines(self) -> None:
        """Skip newline tokens."""
        while self._current().type == TokenType.NEWLINE:
            self._advance()

    def _expect(self, token_type: TokenType, error_msg: str) -> Token:
        """Expect a specific token type."""
        self._skip_newlines()
        token = self._current()
        if token.type != token_type:
            raise PolicyParseError(
                f"{error_msg}. Expected {token_type.value}, got {token.type.value}",
                token.line,
                token.column,
            )
        return self._advance()

    def _parse_policy_declaration(self) -> str:
        """Parse POLICY <name>."""
        self._skip_newlines()
        self._expect(TokenType.POLICY, "Expected POLICY keyword")
        name_token = self._expect(TokenType.IDENTIFIER, "Expected policy name")
        return name_token.value

    def _parse_domain(self) -> str:
        """Parse DOMAIN <domain>."""
        self._skip_newlines()
        self._expect(TokenType.DOMAIN, "Expected DOMAIN keyword")
        self._skip_newlines()
        domain_token = self._current()
        if domain_token.type == TokenType.IDENTIFIER:
            self._advance()
            return domain_token.value
        elif domain_token.type == TokenType.STRING:
            self._advance()
            return domain_token.value
        raise PolicyParseError(
            "Expected domain name", domain_token.line, domain_token.column
        )

    def _parse_gate(self) -> str:
        """Parse GATE <gate>."""
        self._skip_newlines()
        self._expect(TokenType.GATE, "Expected GATE keyword")
        gate_token = self._expect(TokenType.IDENTIFIER, "Expected gate (G1, G2, etc.)")
        return gate_token.value

    def _parse_requirements(self) -> List[RequireCondition]:
        """Parse all REQUIRE statements."""
        requirements = []
        while True:
            self._skip_newlines()
            if self._current().type != TokenType.REQUIRE:
                break
            self._advance()  # consume REQUIRE

            # Parse field
            field_token = self._expect(TokenType.IDENTIFIER, "Expected field name")
            field = field_token.value

            # Check for special "no_contradiction" type requirements
            if field == "no_contradiction":
                # Optional modifier (weak/strong)
                modifier = None
                self._skip_newlines()
                if self._current().type == TokenType.IDENTIFIER:
                    modifier = self._current().value
                    self._advance()
                requirements.append(
                    RequireCondition(
                        field=field,
                        operator="=",
                        value=True,
                        modifier=modifier,
                    )
                )
                continue

            if field == "temporal_consistency":
                requirements.append(
                    RequireCondition(
                        field=field,
                        operator="=",
                        value=True,
                    )
                )
                continue

            # Parse operator
            op_token = self._current()
            if op_token.type in (
                TokenType.GTE,
                TokenType.LTE,
                TokenType.GT,
                TokenType.LT,
                TokenType.EQ,
                TokenType.NEQ,
            ):
                self._advance()
                operator = op_token.value
            else:
                raise PolicyParseError(
                    f"Expected comparison operator, got {op_token.type.value}",
                    op_token.line,
                    op_token.column,
                )

            # Parse value
            value_token = self._current()
            if value_token.type == TokenType.NUMBER:
                value = value_token.value
                self._advance()
            elif value_token.type == TokenType.STRING:
                value = value_token.value
                self._advance()
            elif value_token.type == TokenType.IDENTIFIER:
                value = value_token.value
                self._advance()
            else:
                raise PolicyParseError(
                    "Expected value", value_token.line, value_token.column
                )

            # Check for modifier
            modifier = None
            self._skip_newlines()
            if (
                self._current().type == TokenType.IDENTIFIER
                and self._current().value.lower() in KNOWN_MODIFIERS
            ):
                modifier = self._current().value
                self._advance()

            requirements.append(
                RequireCondition(
                    field=field,
                    operator=operator,
                    value=value,
                    modifier=modifier,
                )
            )

        return requirements

    def _parse_rules(self) -> List[OnThenRule]:
        """Parse all ON...THEN rules."""
        rules = []
        while True:
            self._skip_newlines()
            if self._current().type != TokenType.ON:
                break
            self._advance()  # consume ON

            # Parse condition
            self._skip_newlines()
            condition_token = self._current()

            # Simple condition (known condition name)
            if (
                condition_token.type == TokenType.IDENTIFIER
                and condition_token.value in KNOWN_CONDITIONS
            ):
                self._advance()
                condition_field = condition_token.value
                condition_operator = "="
                condition_value = True
            else:
                # Complex condition: field op value
                field_token = self._expect(TokenType.IDENTIFIER, "Expected condition field")
                condition_field = field_token.value

                op_token = self._current()
                if op_token.type in (
                    TokenType.GTE,
                    TokenType.LTE,
                    TokenType.GT,
                    TokenType.LT,
                    TokenType.EQ,
                    TokenType.NEQ,
                ):
                    self._advance()
                    condition_operator = op_token.value
                else:
                    condition_operator = "="

                value_token = self._current()
                if value_token.type in (TokenType.NUMBER, TokenType.STRING, TokenType.IDENTIFIER):
                    condition_value = value_token.value
                    self._advance()
                else:
                    condition_value = True

            # Parse THEN
            self._skip_newlines()
            self._expect(TokenType.THEN, "Expected THEN keyword")

            # Parse action
            self._skip_newlines()
            action_token = self._expect(TokenType.IDENTIFIER, "Expected action name")
            action = action_token.value
            action_params = {}

            # Check for action parameters (e.g., committee_quorum(3))
            if self._current().type == TokenType.LPAREN:
                self._advance()
                if self._current().type == TokenType.NUMBER:
                    action_params["quorum"] = self._current().value
                    self._advance()
                self._expect(TokenType.RPAREN, "Expected closing parenthesis")

            rules.append(
                OnThenRule(
                    condition_field=condition_field,
                    condition_operator=condition_operator,
                    condition_value=condition_value,
                    action=action,
                    action_params=action_params,
                )
            )

        return rules

    def _parse_version(self) -> str:
        """Parse VERSION "<version>"."""
        self._skip_newlines()
        if self._current().type == TokenType.VERSION:
            self._advance()
            version_token = self._expect(TokenType.STRING, "Expected version string")
            return version_token.value
        return "1.0.0"


def parse_policy(text: str) -> PolicyAST:
    """
    Convenience function to parse a policy.

    Args:
        text: Policy DSL text

    Returns:
        PolicyAST

    Raises:
        PolicyParseError: If parsing fails
    """
    parser = PolicyParser()
    return parser.parse(text)
