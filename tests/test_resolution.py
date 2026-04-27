# test_resolution.py — Unit tests for resolution-based entailment
#
# Tests:
#   - Simple entailment: {p, p→q} ⊨ q
#   - Non-entailment: {p} ⊭ q
#   - Contradiction detection: {p, ¬p} ⊨ anything
#   - Tautology: ⊨ p ∨ ¬p
#   - Larger knowledge bases with multiple resolution steps

import pytest
from src.logic.syntax import Atom, Not, And, Or, Implies, parse
from src.logic.cnf import to_cnf
from src.logic.resolution import entails, resolve, entails_from_formulas


class TestResolve:
    def test_complementary_pair(self):
        c1 = frozenset({"p", "q"})
        c2 = frozenset({"~p", "r"})
        result = resolve(c1, c2)
        assert frozenset({"q", "r"}) in result

    def test_no_complement(self):
        c1 = frozenset({"p", "q"})
        c2 = frozenset({"r", "s"})
        assert resolve(c1, c2) == set()

    def test_empty_clause(self):
        c1 = frozenset({"p"})
        c2 = frozenset({"~p"})
        result = resolve(c1, c2)
        assert frozenset() in result

    def test_tautology_filtered(self):
        # {p, q} resolved with {~p, ~q} on p gives {q, ~q} — tautology, filtered
        c1 = frozenset({"p", "q"})
        c2 = frozenset({"~p", "~q"})
        result = resolve(c1, c2)
        # Resolving on p: {q, ~q} — tautology (filtered)
        # Resolving on q: {p, ~p} — tautology (filtered)
        assert frozenset() not in result


class TestEntails:
    def test_modus_ponens(self):
        # {p, p→q} ⊨ q
        kb = to_cnf(Atom("p")) | to_cnf(Implies(Atom("p"), Atom("q")))
        assert entails(kb, Atom("q")) is True

    def test_non_entailment(self):
        # {p} ⊭ q
        kb = to_cnf(Atom("p"))
        assert entails(kb, Atom("q")) is False

    def test_contradiction_entails_anything(self):
        # {p, ¬p} ⊨ q  (explosion / ex falso)
        kb = to_cnf(Atom("p")) | to_cnf(Not(Atom("p")))
        assert entails(kb, Atom("q")) is True

    def test_tautology(self):
        # {} ⊨ p ∨ ¬p  — tautology is always entailed
        kb: set[frozenset[str]] = set()
        taut = Or(Atom("p"), Not(Atom("p")))
        assert entails(kb, taut) is True

    def test_chain_reasoning(self):
        # {p, p→q, q→r} ⊨ r
        kb = (to_cnf(Atom("p"))
              | to_cnf(Implies(Atom("p"), Atom("q")))
              | to_cnf(Implies(Atom("q"), Atom("r"))))
        assert entails(kb, Atom("r")) is True

    def test_chain_non_entailment(self):
        # {p, p→q, q→r} ⊭ s
        kb = (to_cnf(Atom("p"))
              | to_cnf(Implies(Atom("p"), Atom("q")))
              | to_cnf(Implies(Atom("q"), Atom("r"))))
        assert entails(kb, Atom("s")) is False

    def test_disjunctive_syllogism(self):
        # {p ∨ q, ¬p} ⊨ q
        kb = to_cnf(Or(Atom("p"), Atom("q"))) | to_cnf(Not(Atom("p")))
        assert entails(kb, Atom("q")) is True


class TestEntailsFromFormulas:
    def test_convenience_wrapper(self):
        formulas = [Atom("p"), Implies(Atom("p"), Atom("q"))]
        assert entails_from_formulas(formulas, Atom("q")) is True
        assert entails_from_formulas(formulas, Atom("r")) is False
