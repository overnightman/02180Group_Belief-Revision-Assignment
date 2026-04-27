# test_revision.py — Unit tests for AGM belief revision
#
# Tests:
#   - Revising with a consistent formula → formula in the base
#   - Revising with a contradictory formula → old contradicting beliefs removed
#   - Levi identity correctness: revision = contraction(¬φ) + expansion(φ)

import pytest
from src.logic.syntax import Atom, Not, Implies, And, Or
from src.belief_base.belief_base import BeliefBase
from src.belief_base.revision import revise
from src.belief_base.contraction import contract


class TestRevision:
    def test_success_postulate(self):
        """After revision B*φ, the formula φ should be in the base."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        result = revise(bb, Atom("q"), 1.0)
        assert Atom("q") in result

    def test_revise_consistent_formula(self):
        """Revising with a consistent formula should keep other beliefs."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 1.0)
        result = revise(bb, Atom("r"), 1.0)
        assert Atom("r") in result
        # p and q should still be present (no contradiction)
        assert Atom("p") in result
        assert Atom("q") in result

    def test_revise_contradictory_formula(self):
        """Revising with ¬p when p is believed should remove p."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 2.0)
        result = revise(bb, Not(Atom("p")), 3.0)
        # ¬p should be in the result
        assert Not(Atom("p")) in result
        # The result should be consistent
        assert result.is_consistent()

    def test_levi_identity(self):
        """B*φ should equal (B÷¬φ)+φ (the Levi identity)."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Implies(Atom("p"), Atom("q")), 2.0)

        phi = Atom("r")

        # Method 1: revise directly
        revised = revise(bb, phi, 1.0)

        # Method 2: Levi identity manually
        contracted = contract(bb, Not(phi))
        contracted.add(phi, 1.0)

        # Both should contain φ
        assert phi in revised
        assert phi in contracted

        # Both should have the same formulas
        assert set(revised.get_formulas()) == set(contracted.get_formulas())

    def test_revise_empty_base(self):
        """Revising an empty base should just add the formula."""
        bb = BeliefBase()
        result = revise(bb, Atom("p"), 1.0)
        assert Atom("p") in result
        assert len(result) == 1

    def test_successive_revisions(self):
        """Multiple revisions should work correctly."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb = revise(bb, Atom("q"), 1.0)
        bb = revise(bb, Not(Atom("p")), 2.0)
        assert Not(Atom("p")) in bb
        assert Atom("q") in bb
        assert bb.is_consistent()
