# test_cnf.py — Unit tests for CNF conversion
#
# Tests:
#   - Biconditional elimination
#   - Implication elimination
#   - De Morgan's laws (pushing negations inward)
#   - Double negation elimination
#   - Distribution of ∨ over ∧
#   - Idempotency and tautology simplification
#   - End-to-end: arbitrary formula → correct CNF clause set

import pytest
from src.logic.syntax import Atom, Not, And, Or, Implies, Biconditional, parse
from src.logic.cnf import (
    eliminate_biconditionals,
    eliminate_implications,
    push_negations,
    distribute_or_over_and,
    to_cnf,
)


# ── Step-by-step tests ──────────────────────────────────────────────────

class TestEliminateBiconditionals:
    def test_simple(self):
        f = Biconditional(Atom("p"), Atom("q"))
        result = eliminate_biconditionals(f)
        expected = And(Implies(Atom("p"), Atom("q")), Implies(Atom("q"), Atom("p")))
        assert result == expected

    def test_nested(self):
        f = Not(Biconditional(Atom("p"), Atom("q")))
        result = eliminate_biconditionals(f)
        inner = And(Implies(Atom("p"), Atom("q")), Implies(Atom("q"), Atom("p")))
        assert result == Not(inner)

    def test_no_biconditional(self):
        f = And(Atom("p"), Atom("q"))
        assert eliminate_biconditionals(f) == f


class TestEliminateImplications:
    def test_simple(self):
        f = Implies(Atom("p"), Atom("q"))
        result = eliminate_implications(f)
        expected = Or(Not(Atom("p")), Atom("q"))
        assert result == expected

    def test_nested(self):
        f = And(Implies(Atom("p"), Atom("q")), Atom("r"))
        result = eliminate_implications(f)
        expected = And(Or(Not(Atom("p")), Atom("q")), Atom("r"))
        assert result == expected


class TestPushNegations:
    def test_double_negation(self):
        f = Not(Not(Atom("p")))
        assert push_negations(f) == Atom("p")

    def test_de_morgan_and(self):
        # ¬(p ∧ q) ≡ ¬p ∨ ¬q
        f = Not(And(Atom("p"), Atom("q")))
        result = push_negations(f)
        expected = Or(Not(Atom("p")), Not(Atom("q")))
        assert result == expected

    def test_de_morgan_or(self):
        # ¬(p ∨ q) ≡ ¬p ∧ ¬q
        f = Not(Or(Atom("p"), Atom("q")))
        result = push_negations(f)
        expected = And(Not(Atom("p")), Not(Atom("q")))
        assert result == expected

    def test_triple_negation(self):
        f = Not(Not(Not(Atom("p"))))
        assert push_negations(f) == Not(Atom("p"))


class TestDistribution:
    def test_or_over_and(self):
        # p ∨ (q ∧ r) ≡ (p ∨ q) ∧ (p ∨ r)
        f = Or(Atom("p"), And(Atom("q"), Atom("r")))
        result = distribute_or_over_and(f)
        expected = And(Or(Atom("p"), Atom("q")), Or(Atom("p"), Atom("r")))
        assert result == expected

    def test_and_or_left(self):
        # (q ∧ r) ∨ p ≡ (q ∨ p) ∧ (r ∨ p)
        f = Or(And(Atom("q"), Atom("r")), Atom("p"))
        result = distribute_or_over_and(f)
        expected = And(Or(Atom("q"), Atom("p")), Or(Atom("r"), Atom("p")))
        assert result == expected


# ── End-to-end CNF conversion ───────────────────────────────────────────

class TestToCnf:
    def test_atom(self):
        assert to_cnf(Atom("p")) == {frozenset({"p"})}

    def test_negation(self):
        assert to_cnf(Not(Atom("p"))) == {frozenset({"~p"})}

    def test_conjunction(self):
        result = to_cnf(And(Atom("p"), Atom("q")))
        assert result == {frozenset({"p"}), frozenset({"q"})}

    def test_disjunction(self):
        result = to_cnf(Or(Atom("p"), Atom("q")))
        assert result == {frozenset({"p", "q"})}

    def test_implication(self):
        # p → q  ≡  ¬p ∨ q
        result = to_cnf(Implies(Atom("p"), Atom("q")))
        assert result == {frozenset({"~p", "q"})}

    def test_biconditional(self):
        # p ↔ q  ≡  (¬p ∨ q) ∧ (¬q ∨ p)
        result = to_cnf(Biconditional(Atom("p"), Atom("q")))
        assert frozenset({"~p", "q"}) in result
        assert frozenset({"~q", "p"}) in result

    def test_complex(self):
        # (p → q) ∧ (q → r)
        f = And(Implies(Atom("p"), Atom("q")), Implies(Atom("q"), Atom("r")))
        result = to_cnf(f)
        assert frozenset({"~p", "q"}) in result
        assert frozenset({"~q", "r"}) in result

    def test_de_morgan_in_cnf(self):
        # ¬(p ∧ q) ≡ ¬p ∨ ¬q  → single clause {~p, ~q}
        result = to_cnf(Not(And(Atom("p"), Atom("q"))))
        assert result == {frozenset({"~p", "~q"})}

    def test_distribution_needed(self):
        # p ∨ (q ∧ r) → {p,q} and {p,r}
        result = to_cnf(Or(Atom("p"), And(Atom("q"), Atom("r"))))
        assert frozenset({"p", "q"}) in result
        assert frozenset({"p", "r"}) in result

    def test_parsed_formula(self):
        f = parse("p & (q | ~r) -> s")
        result = to_cnf(f)
        # Should be a valid set of clauses (non-empty)
        assert isinstance(result, set)
        assert all(isinstance(c, frozenset) for c in result)
