"""
Tests for Truth Policy DSL Parser — S37

Tests for policy lexer and parser.
"""

import pytest

from app.truth.policy_dsl.parser import (
    PolicyLexer,
    PolicyParseError,
    PolicyParser,
    parse_policy,
)
from app.truth.policy_dsl.grammar import TokenType


class TestPolicyParseError:
    """Tests for PolicyParseError exception."""

    def test_create(self):
        """Create parse error."""
        error = PolicyParseError("Test error", line=5, column=10)

        assert error.message == "Test error"
        assert error.line == 5
        assert error.column == 10
        assert "Line 5" in str(error)
        assert "Col 10" in str(error)

    def test_default_position(self):
        """Default position is 0."""
        error = PolicyParseError("Test")

        assert error.line == 0
        assert error.column == 0


class TestPolicyLexer:
    """Tests for PolicyLexer class."""

    def test_tokenize_empty(self):
        """Tokenize empty string."""
        lexer = PolicyLexer("")
        tokens = lexer.tokenize()

        assert len(tokens) == 1
        assert tokens[0].type == TokenType.EOF

    def test_tokenize_keywords(self):
        """Tokenize keywords."""
        lexer = PolicyLexer("POLICY DOMAIN GATE REQUIRE ON THEN VERSION")
        tokens = lexer.tokenize()

        types = [t.type for t in tokens[:-1]]  # Exclude EOF
        assert TokenType.POLICY in types
        assert TokenType.DOMAIN in types
        assert TokenType.GATE in types
        assert TokenType.REQUIRE in types
        assert TokenType.ON in types
        assert TokenType.THEN in types
        assert TokenType.VERSION in types

    def test_tokenize_keywords_case_insensitive(self):
        """Keywords are case insensitive."""
        lexer = PolicyLexer("policy domain GATE Require")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.POLICY
        assert tokens[1].type == TokenType.DOMAIN
        assert tokens[2].type == TokenType.GATE
        assert tokens[3].type == TokenType.REQUIRE

    def test_tokenize_operators(self):
        """Tokenize operators."""
        lexer = PolicyLexer(">= <= > < = !=")
        tokens = lexer.tokenize()

        types = [t.type for t in tokens[:-1]]
        assert TokenType.GTE in types
        assert TokenType.LTE in types
        assert TokenType.GT in types
        assert TokenType.LT in types
        assert TokenType.EQ in types
        assert TokenType.NEQ in types

    def test_tokenize_symbols(self):
        """Tokenize symbols."""
        lexer = PolicyLexer("{ } ( ) ; ,")
        tokens = lexer.tokenize()

        types = [t.type for t in tokens[:-1]]
        assert TokenType.LBRACE in types
        assert TokenType.RBRACE in types
        assert TokenType.LPAREN in types
        assert TokenType.RPAREN in types
        assert TokenType.SEMICOLON in types
        assert TokenType.COMMA in types

    def test_tokenize_string_double_quotes(self):
        """Tokenize double-quoted string."""
        lexer = PolicyLexer('"hello world"')
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"

    def test_tokenize_string_single_quotes(self):
        """Tokenize single-quoted string."""
        lexer = PolicyLexer("'hello world'")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == "hello world"

    def test_tokenize_string_escaped(self):
        """Tokenize string with escape."""
        lexer = PolicyLexer('"hello\\"world"')
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.STRING
        assert tokens[0].value == 'hello"world'

    def test_tokenize_string_unterminated(self):
        """Raises error on unterminated string."""
        lexer = PolicyLexer('"hello')

        with pytest.raises(PolicyParseError, match="Unterminated string"):
            lexer.tokenize()

    def test_tokenize_number_integer(self):
        """Tokenize integer."""
        lexer = PolicyLexer("42")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42

    def test_tokenize_number_float(self):
        """Tokenize float."""
        lexer = PolicyLexer("3.14")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14

    def test_tokenize_identifier(self):
        """Tokenize identifier."""
        lexer = PolicyLexer("sources evidence_count")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "sources"
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "evidence_count"

    def test_tokenize_newline(self):
        """Tokenize newline."""
        lexer = PolicyLexer("a\nb")
        tokens = lexer.tokenize()

        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].type == TokenType.IDENTIFIER

    def test_skip_whitespace(self):
        """Skip whitespace."""
        lexer = PolicyLexer("  \t  a   ")
        tokens = lexer.tokenize()

        assert len(tokens) == 2  # identifier + EOF
        assert tokens[0].value == "a"

    def test_skip_comments(self):
        """Skip comments."""
        lexer = PolicyLexer("a # this is a comment\nb")
        tokens = lexer.tokenize()

        # a, newline, b, EOF
        assert tokens[0].value == "a"
        assert tokens[1].type == TokenType.NEWLINE
        assert tokens[2].value == "b"

    def test_unexpected_character(self):
        """Raises error on unexpected character."""
        lexer = PolicyLexer("@")

        with pytest.raises(PolicyParseError, match="Unexpected character"):
            lexer.tokenize()

    def test_line_column_tracking(self):
        """Track line and column numbers."""
        lexer = PolicyLexer("a\nb c")
        tokens = lexer.tokenize()

        assert tokens[0].line == 1
        assert tokens[0].column == 1
        assert tokens[2].line == 2
        assert tokens[2].column == 1
        assert tokens[3].line == 2
        assert tokens[3].column == 3

    def test_tokenize_logical_operators(self):
        """Tokenize logical operators."""
        lexer = PolicyLexer("AND OR NOT")
        tokens = lexer.tokenize()

        types = [t.type for t in tokens[:-1]]
        assert TokenType.AND in types
        assert TokenType.OR in types
        assert TokenType.NOT in types


class TestPolicyParser:
    """Tests for PolicyParser class."""

    def test_parse_minimal_policy(self):
        """Parse minimal valid policy."""
        text = """
        POLICY test_policy
        DOMAIN politics
        GATE G1
        REQUIRE sources >= 1
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.name == "test_policy"
        assert ast.domain == "politics"
        assert ast.gate == "G1"
        assert len(ast.requirements) == 1

    def test_parse_policy_with_string_domain(self):
        """Parse policy with string domain."""
        text = """
        POLICY test
        DOMAIN "my-domain"
        GATE G1
        REQUIRE sources >= 1
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.domain == "my-domain"

    def test_parse_requirements(self):
        """Parse multiple requirements."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 2
        REQUIRE evidence_count >= 1
        REQUIRE confidence = "high"
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert len(ast.requirements) == 3
        assert ast.requirements[0].field == "sources"
        assert ast.requirements[0].operator == ">="
        assert ast.requirements[0].value == 2
        assert ast.requirements[2].value == "high"

    def test_parse_no_contradiction(self):
        """Parse no_contradiction requirement."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE no_contradiction
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.requirements[0].field == "no_contradiction"
        assert ast.requirements[0].operator == "="
        assert ast.requirements[0].value is True

    def test_parse_no_contradiction_with_modifier(self):
        """Parse no_contradiction with modifier."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE no_contradiction strong
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.requirements[0].modifier == "strong"

    def test_parse_temporal_consistency(self):
        """Parse temporal_consistency requirement."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE temporal_consistency
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.requirements[0].field == "temporal_consistency"

    def test_parse_requirement_with_modifier(self):
        """Parse requirement with modifier."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 2 independent
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.requirements[0].modifier == "independent"

    def test_parse_rules_known_condition(self):
        """Parse rule with known condition."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON high_confidence THEN auto_approve
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert len(ast.rules) == 1
        assert ast.rules[0].condition_field == "high_confidence"
        assert ast.rules[0].action == "auto_approve"

    def test_parse_rules_field_comparison(self):
        """Parse rule with field comparison."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON evidence_count < 3 THEN human_review
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.rules[0].condition_field == "evidence_count"
        assert ast.rules[0].condition_operator == "<"
        assert ast.rules[0].condition_value == 3
        assert ast.rules[0].action == "human_review"

    def test_parse_rules_with_params(self):
        """Parse rule with action parameters."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        ON disputed THEN committee_quorum(5)
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.rules[0].action_params["quorum"] == 5

    def test_parse_version(self):
        """Parse version."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        VERSION "2.0.0"
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.version == "2.0.0"

    def test_parse_default_version(self):
        """Default version is 1.0.0."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        """

        parser = PolicyParser()
        ast = parser.parse(text)

        assert ast.version == "1.0.0"

    def test_parse_error_missing_policy(self):
        """Error on missing POLICY keyword."""
        text = "DOMAIN test"

        parser = PolicyParser()
        with pytest.raises(PolicyParseError, match="Expected POLICY"):
            parser.parse(text)

    def test_parse_error_missing_domain(self):
        """Error on missing DOMAIN keyword."""
        text = "POLICY test\nGATE G1"

        parser = PolicyParser()
        with pytest.raises(PolicyParseError, match="Expected DOMAIN"):
            parser.parse(text)

    def test_parse_error_missing_gate(self):
        """Error on missing GATE keyword."""
        text = "POLICY test\nDOMAIN test"

        parser = PolicyParser()
        with pytest.raises(PolicyParseError, match="Expected GATE"):
            parser.parse(text)

    def test_parse_error_invalid_operator(self):
        """Error on invalid operator in requirement."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources bad 2
        """

        parser = PolicyParser()
        with pytest.raises(PolicyParseError, match="Expected comparison operator"):
            parser.parse(text)


class TestParsePolicy:
    """Tests for parse_policy convenience function."""

    def test_parse_policy_function(self):
        """Convenience function works."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        """

        ast = parse_policy(text)

        assert ast.name == "test"
        assert ast.domain == "test"

    def test_parse_full_policy(self):
        """Parse complete policy."""
        text = """
        # This is a comment
        POLICY strict_politics
        DOMAIN politics
        GATE G2

        # Requirements
        REQUIRE sources >= 3 independent
        REQUIRE evidence_count >= 2
        REQUIRE no_contradiction strong

        # Rules
        ON high_confidence THEN auto_approve
        ON low_confidence THEN human_review
        ON disputed THEN committee_quorum(3)
        ON evidence_count < 1 THEN auto_reject

        VERSION "3.0.0"
        """

        ast = parse_policy(text)

        assert ast.name == "strict_politics"
        assert ast.domain == "politics"
        assert ast.gate == "G2"
        assert len(ast.requirements) == 3
        assert len(ast.rules) == 4
        assert ast.version == "3.0.0"

    def test_parse_policy_with_all_operators(self):
        """Parse policy with all comparison operators."""
        text = """
        POLICY test
        DOMAIN test
        GATE G1
        REQUIRE sources >= 1
        REQUIRE evidence_count <= 10
        REQUIRE risk_level > 0
        REQUIRE claim_age_hours < 24
        REQUIRE confidence = "high"
        REQUIRE status != "rejected"
        """

        ast = parse_policy(text)

        operators = [r.operator for r in ast.requirements]
        assert ">=" in operators
        assert "<=" in operators
        assert ">" in operators
        assert "<" in operators
        assert "=" in operators
        assert "!=" in operators


class TestLexerPeek:
    """Tests for lexer _peek method edge cases."""

    def test_peek_at_end_of_text(self):
        """Peek returns empty when at end of text."""
        lexer = PolicyLexer("x")
        lexer.pos = 0  # At 'x'
        assert lexer._peek() == ""  # Nothing after 'x'

    def test_peek_beyond_end(self):
        """Peek returns empty when beyond text."""
        lexer = PolicyLexer("ab")
        lexer.pos = 1  # At 'b'
        assert lexer._peek() == ""  # Nothing after 'b'


class TestParserEOFHandling:
    """Tests for parser EOF handling."""

    def test_current_at_eof(self):
        """_current returns EOF when past tokens."""
        parser = PolicyParser()
        parser.tokens = []  # Empty tokens
        parser.pos = 0
        token = parser._current()
        assert token.type == TokenType.EOF

    def test_peek_at_eof(self):
        """_peek returns EOF when peeking past tokens."""
        from app.truth.policy_dsl.parser import Token
        parser = PolicyParser()
        token1 = Token(TokenType.IDENTIFIER, "test", 1, 1)
        parser.tokens = [token1]
        parser.pos = 0

        # Peek beyond available tokens
        eof_token = parser._peek(5)
        assert eof_token.type == TokenType.EOF

    def test_peek_at_last_token(self):
        """_peek returns EOF when peeking from last token."""
        from app.truth.policy_dsl.parser import Token
        parser = PolicyParser()
        token1 = Token(TokenType.IDENTIFIER, "test", 1, 1)
        parser.tokens = [token1]
        parser.pos = 0

        # Peek 1 beyond last token
        eof_token = parser._peek(1)
        assert eof_token.type == TokenType.EOF


class TestParserErrorPositions:
    """Tests for parser error with positions."""

    def test_unexpected_token_includes_position(self):
        """Unexpected token error includes line and column."""
        text = """
        POLICY test
        DOMAIN test
        GATE
        """
        # GATE without identifier should fail
        with pytest.raises(PolicyParseError) as exc_info:
            parse_policy(text)

        assert exc_info.value.line > 0 or exc_info.value.column >= 0
