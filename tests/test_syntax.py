# test_syntax.py — Unit tests for propositional formula parsing and AST
#
# Tests:
#   - Atom creation and equality
#   - Negation, conjunction, disjunction, implication, biconditional
#   - String-to-AST parsing (operator precedence, parentheses)
#   - Pretty-printing (AST back to string)

import pytest
from src.logic.syntax import (
    Atom, Not, And, Or, Implies, Biconditional, parse, Formula,
)


# ── Atom creation and equality ──────────────────────────────────────────

class TestAtom:
    def test_creation(self):
        p = Atom("p")
        assert p.name == "p"

    def test_equality(self):
        assert Atom("p") == Atom("p")
        assert Atom("p") != Atom("q")

    def test_hash(self):
        assert hash(Atom("p")) == hash(Atom("p"))
        s = {Atom("p"), Atom("p"), Atom("q")}
        assert len(s) == 2

    def test_str(self):
        assert str(Atom("p")) == "p"

    def test_repr(self):
        assert repr(Atom("p")) == "Atom('p')"

    def test_atoms(self):
        assert Atom("p").atoms() == {"p"}


# ── Compound formula construction ───────────────────────────────────────

class TestCompoundFormulas:
    def test_not(self):
        f = Not(Atom("p"))
        assert f.operand == Atom("p")
        assert str(f) == "~p"

    def test_and(self):
        f = And(Atom("p"), Atom("q"))
        assert f.left == Atom("p")
        assert f.right == Atom("q")
        assert str(f) == "p & q"

    def test_or(self):
        f = Or(Atom("p"), Atom("q"))
        assert str(f) == "p | q"

    def test_implies(self):
        f = Implies(Atom("p"), Atom("q"))
        assert str(f) == "p -> q"

    def test_biconditional(self):
        f = Biconditional(Atom("p"), Atom("q"))
        assert str(f) == "p <-> q"

    def test_nested(self):
        f = And(Or(Atom("p"), Atom("q")), Not(Atom("r")))
        assert f.atoms() == {"p", "q", "r"}

    def test_equality(self):
        f1 = And(Atom("p"), Atom("q"))
        f2 = And(Atom("p"), Atom("q"))
        f3 = And(Atom("p"), Atom("r"))
        assert f1 == f2
        assert f1 != f3

    def test_hash_compound(self):
        f1 = Implies(Atom("p"), Atom("q"))
        f2 = Implies(Atom("p"), Atom("q"))
        assert hash(f1) == hash(f2)


# ── Parser ──────────────────────────────────────────────────────────────

class TestParser:
    def test_atom(self):
        assert parse("p") == Atom("p")

    def test_negation(self):
        assert parse("~p") == Not(Atom("p"))

    def test_double_negation(self):
        assert parse("~~p") == Not(Not(Atom("p")))

    def test_conjunction(self):
        assert parse("p & q") == And(Atom("p"), Atom("q"))

    def test_disjunction(self):
        assert parse("p | q") == Or(Atom("p"), Atom("q"))

    def test_implication(self):
        assert parse("p -> q") == Implies(Atom("p"), Atom("q"))

    def test_biconditional(self):
        assert parse("p <-> q") == Biconditional(Atom("p"), Atom("q"))

    def test_precedence_and_over_or(self):
        # p | q & r  should be  p | (q & r)
        result = parse("p | q & r")
        expected = Or(Atom("p"), And(Atom("q"), Atom("r")))
        assert result == expected

    def test_precedence_or_over_implies(self):
        # p -> q | r  should be  p -> (q | r)
        result = parse("p -> q | r")
        expected = Implies(Atom("p"), Or(Atom("q"), Atom("r")))
        assert result == expected

    def test_parentheses(self):
        result = parse("(p | q) & r")
        expected = And(Or(Atom("p"), Atom("q")), Atom("r"))
        assert result == expected

    def test_complex_formula(self):
        result = parse("p & (q | ~r) -> s")
        expected = Implies(
            And(Atom("p"), Or(Atom("q"), Not(Atom("r")))),
            Atom("s"),
        )
        assert result == expected

    def test_implication_right_associative(self):
        # a -> b -> c  should be  a -> (b -> c)
        result = parse("a -> b -> c")
        expected = Implies(Atom("a"), Implies(Atom("b"), Atom("c")))
        assert result == expected

    def test_multichar_atom(self):
        result = parse("rain -> wet")
        expected = Implies(Atom("rain"), Atom("wet"))
        assert result == expected

    def test_invalid_token(self):
        with pytest.raises(ValueError):
            parse("p @ q")

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            parse("")
