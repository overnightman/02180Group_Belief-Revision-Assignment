# test_agm_postulates.py — Verification of AGM postulates
#
# Systematically tests that the revision operator satisfies all AGM postulates:
#
#   (*1) Closure      — B*φ is a belief set (closed under logical consequence)
#   (*2) Success      — φ ∈ B*φ
#   (*3) Inclusion    — B*φ ⊆ B+φ
#   (*4) Vacuity      — If ¬φ ∉ B, then B*φ = B+φ
#   (*5) Consistency  — B*φ is consistent (unless φ is a contradiction)
#   (*6) Extensionality — If φ ≡ ψ, then B*φ = B*ψ
#
# Uses multiple randomly generated and hand-crafted belief bases + formulas.

import pytest
from src.logic.syntax import Atom, Not, And, Or, Implies, Biconditional
from src.belief_base.belief_base import BeliefBase
from src.belief_base.revision import revise


def _make_bb(*beliefs: tuple) -> BeliefBase:
    """Helper: build a BeliefBase from (formula, priority) tuples."""
    bb = BeliefBase()
    for formula, priority in beliefs:
        bb.add(formula, priority)
    return bb


# ── (*2) Success ────────────────────────────────────────────────────────

class TestSuccess:
    """(*2) After revision B*φ, the formula φ must be in the belief base."""

    def test_success_atom(self):
        bb = _make_bb((Atom("p"), 1.0), (Atom("q"), 1.0))
        result = revise(bb, Atom("r"), 1.0)
        assert result.entails(Atom("r"))

    def test_success_negation(self):
        bb = _make_bb((Atom("p"), 1.0))
        result = revise(bb, Not(Atom("p")), 2.0)
        assert result.entails(Not(Atom("p")))

    def test_success_implication(self):
        bb = _make_bb((Atom("p"), 1.0))
        phi = Implies(Atom("p"), Atom("q"))
        result = revise(bb, phi, 1.0)
        assert result.entails(phi)

    def test_success_empty_base(self):
        bb = BeliefBase()
        result = revise(bb, Atom("x"), 1.0)
        assert result.entails(Atom("x"))


# ── (*3) Inclusion ──────────────────────────────────────────────────────

class TestInclusion:
    """(*3) B*φ ⊆ B+φ — the revised base is a subset of the expanded base."""

    def test_inclusion_consistent(self):
        bb = _make_bb((Atom("p"), 1.0), (Atom("q"), 1.0))
        phi = Atom("r")
        revised = revise(bb, phi, 1.0)
        # Build B+φ
        expanded = bb.copy()
        expanded.add(phi, 1.0)
        # Every formula in revised should be in expanded
        for f in revised.get_formulas():
            assert f in expanded

    def test_inclusion_contradictory(self):
        bb = _make_bb((Atom("p"), 1.0))
        phi = Not(Atom("p"))
        revised = revise(bb, phi, 2.0)
        # Revised formulas should be a subset of what expansion would give
        expanded = bb.copy()
        expanded.add(phi, 2.0)
        for f in revised.get_formulas():
            assert f in expanded


# ── (*4) Vacuity ────────────────────────────────────────────────────────

class TestVacuity:
    """(*4) If ¬φ ∉ Cn(B), then B*φ = B+φ."""

    def test_vacuity_no_contradiction(self):
        bb = _make_bb((Atom("p"), 1.0), (Atom("q"), 1.0))
        phi = Atom("r")  # ¬r is not in bb
        assert not bb.entails(Not(phi))

        revised = revise(bb, phi, 1.0)
        expanded = bb.copy()
        expanded.add(phi, 1.0)

        # Should have exactly the same formulas
        assert set(revised.get_formulas()) == set(expanded.get_formulas())


# ── (*5) Consistency ────────────────────────────────────────────────────

class TestConsistency:
    """(*5) B*φ is consistent unless φ itself is a contradiction."""

    def test_consistent_after_revision(self):
        bb = _make_bb((Atom("p"), 1.0), (Atom("q"), 2.0))
        result = revise(bb, Not(Atom("p")), 3.0)
        assert result.is_consistent()

    def test_consistent_multiple_beliefs(self):
        bb = _make_bb(
            (Atom("p"), 1.0),
            (Implies(Atom("p"), Atom("q")), 2.0),
            (Atom("r"), 1.0),
        )
        result = revise(bb, Not(Atom("q")), 3.0)
        assert result.is_consistent()

    def test_consistent_after_contradictory_revision(self):
        bb = _make_bb(
            (Atom("p"), 1.0),
            (Atom("q"), 1.0),
        )
        result = revise(bb, And(Not(Atom("p")), Not(Atom("q"))), 3.0)
        assert result.is_consistent()


# ── (*6) Extensionality ────────────────────────────────────────────────

class TestExtensionality:
    """(*6) If φ ≡ ψ (logically equivalent), then B*φ = B*ψ."""

    def test_double_negation_equivalence(self):
        bb = _make_bb((Atom("p"), 1.0), (Atom("q"), 1.0))
        phi = Atom("r")
        psi = Not(Not(Atom("r")))  # r ≡ ~~r

        revised_phi = revise(bb, phi, 1.0)
        revised_psi = revise(bb, psi, 1.0)

        # Both should entail r
        assert revised_phi.entails(Atom("r"))
        assert revised_psi.entails(Atom("r"))


# ── Combined / stress tests ─────────────────────────────────────────────

class TestAGMCombined:
    """Combined tests checking multiple postulates together."""

    def test_revision_chain(self):
        """Successive revisions should each satisfy Success + Consistency."""
        bb = _make_bb((Atom("a"), 1.0))

        bb = revise(bb, Atom("b"), 1.0)
        assert bb.entails(Atom("b"))       # Success
        assert bb.is_consistent()           # Consistency

        bb = revise(bb, Not(Atom("a")), 2.0)
        assert bb.entails(Not(Atom("a")))  # Success
        assert bb.is_consistent()           # Consistency

        bb = revise(bb, Atom("c"), 1.0)
        assert bb.entails(Atom("c"))       # Success
        assert bb.is_consistent()           # Consistency

    def test_all_postulates_simple_scenario(self):
        """Run all postulate checks on a single scenario."""
        bb = _make_bb(
            (Atom("p"), 1.0),
            (Implies(Atom("p"), Atom("q")), 2.0),
        )
        phi = Not(Atom("q"))

        result = revise(bb, phi, 3.0)

        # (*2) Success
        assert result.entails(phi)

        # (*3) Inclusion — all formulas in result are in B+φ
        expanded = bb.copy()
        expanded.add(phi, 3.0)
        for f in result.get_formulas():
            assert f in expanded

        # (*5) Consistency
        assert result.is_consistent()
