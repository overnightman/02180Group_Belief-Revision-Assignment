# test_contraction.py — Unit tests for partial meet contraction
#
# Tests:
#   - Contracting a belief that is entailed → belief removed
#   - Contracting a belief not in the base → base unchanged
#   - Priority ordering influences which formulas are kept
#   - Remainder set computation correctness

import pytest
from src.logic.syntax import Atom, Not, Implies, And, Or, parse
from src.belief_base.belief_base import BeliefBase
from src.belief_base.contraction import contract, remainder_sets


class TestContraction:
    def test_contract_entailed_belief(self):
        """Contracting an entailed belief should remove it."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Implies(Atom("p"), Atom("q")), 1.0)
        # BB entails q; after contracting q, it should not entail q
        result = contract(bb, Atom("q"))
        assert not result.entails(Atom("q"))

    def test_contract_not_entailed(self):
        """Contracting a non-entailed belief → base unchanged (vacuity)."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 1.0)
        result = contract(bb, Atom("r"))
        assert result.entails(Atom("p"))
        assert result.entails(Atom("q"))

    def test_contract_preserves_other_beliefs(self):
        """Contraction should keep beliefs not involved in entailing φ."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)
        bb.add(Atom("q"), 1.0)
        bb.add(Implies(Atom("p"), Atom("r")), 1.0)
        result = contract(bb, Atom("r"))
        # q should still be present (it's unrelated)
        assert Atom("q") in result

    def test_priority_influences_kept_beliefs(self):
        """Higher-priority beliefs should survive contraction."""
        bb = BeliefBase()
        bb.add(Atom("p"), 1.0)  # low priority
        bb.add(Implies(Atom("p"), Atom("q")), 5.0)  # high priority
        result = contract(bb, Atom("q"))
        # The high-priority implication should be kept over the low-priority p
        assert not result.entails(Atom("q"))

    def test_contract_empty_base(self):
        """Contracting from an empty base should return an empty base."""
        bb = BeliefBase()
        result = contract(bb, Atom("p"))
        assert len(result) == 0


class TestRemainderSets:
    def test_full_base_not_entailing(self):
        """If the base doesn't entail φ, the only remainder is the full base."""
        beliefs = [(Atom("p"), 1.0), (Atom("q"), 1.0)]
        rems = remainder_sets(beliefs, Atom("r"))
        assert len(rems) == 1
        assert len(rems[0]) == 2

    def test_single_belief_entailing(self):
        """If a single belief entails φ, removing it is the only remainder."""
        beliefs = [(Atom("p"), 1.0)]
        rems = remainder_sets(beliefs, Atom("p"))
        assert len(rems) == 1
        assert len(rems[0]) == 0  # empty remainder

    def test_multiple_remainders(self):
        """Two beliefs jointly entail φ → two maximal remainders."""
        # {p, p→q} ⊨ q.  Remainders: {p} and {p→q}
        beliefs = [
            (Atom("p"), 1.0),
            (Implies(Atom("p"), Atom("q")), 1.0),
        ]
        rems = remainder_sets(beliefs, Atom("q"))
        assert len(rems) == 2
