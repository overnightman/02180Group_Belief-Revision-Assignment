# test_belief_base.py — Unit tests for the belief base data structure
#
# Tests:
#   - Adding / removing formulas
#   - Priority assignment and retrieval
#   - Consistency checking
#   - Entailment queries via the belief base interface

import pytest
from src.logic.syntax import Atom, Not, Implies, And, Or, parse
from src.belief_base.belief_base import BeliefBase


class TestBeliefBaseBasics:
    def test_add_and_len(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        assert len(bb) == 1
        bb.add(Atom("q"), 2.0)
        assert len(bb) == 2

    def test_add_duplicate_updates_priority(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("p"), 5.0)
        assert len(bb) == 1
        beliefs = bb.get_beliefs()
        assert beliefs[0][1] == 5.0

    def test_remove(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 2.0)
        bb.remove(Atom("p"))
        assert len(bb) == 1
        assert Atom("p") not in bb
        assert Atom("q") in bb

    def test_remove_nonexistent(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.remove(Atom("q"))  # should not raise
        assert len(bb) == 1

    def test_contains(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        assert Atom("p") in bb
        assert Atom("q") not in bb

    def test_get_formulas(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 2.0)
        formulas = bb.get_formulas()
        assert Atom("p") in formulas
        assert Atom("q") in formulas

    def test_get_beliefs(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 3.0)
        beliefs = bb.get_beliefs()
        assert beliefs == [(Atom("p"), 3.0)]

    def test_clear(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.clear()
        assert len(bb) == 0

    def test_copy(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb2 = bb.copy()
        bb2.add(Atom("q"), 2.0)
        assert len(bb) == 1
        assert len(bb2) == 2


class TestBeliefBaseLogic:
    def test_entails_simple(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Implies(Atom("p"), Atom("q")), 1.0)
        assert bb.entails(Atom("q")) is True

    def test_does_not_entail(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        assert bb.entails(Atom("q")) is False

    def test_empty_base_entails_nothing(self):
        bb = BeliefBase()
        assert bb.entails(Atom("p")) is False

    def test_consistent_base(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 1.0)
        assert bb.is_consistent() is True

    def test_inconsistent_base(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Not(Atom("p")), 1.0)
        assert bb.is_consistent() is False

    def test_empty_base_is_consistent(self):
        bb = BeliefBase()
        assert bb.is_consistent() is True

    def test_cnf_clauses(self):
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Implies(Atom("p"), Atom("q")), 1.0)
        clauses = bb.to_cnf_clauses()
        assert frozenset({"p"}) in clauses
        assert frozenset({"~p", "q"}) in clauses
