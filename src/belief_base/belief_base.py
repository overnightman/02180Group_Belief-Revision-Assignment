# belief_base.py — Core belief base data structure
#
# A belief base is a finite set of propositional formulas, each annotated
# with a priority / entrenchment degree (integer or float).
#
# Key responsibilities:
#   - Store (formula, priority) pairs
#   - Expose the logical closure via the entailment engine (resolution.py)
#   - Provide helpers: add, remove, contains, is_consistent, etc.
#   - Convert the entire base to a single CNF clause-set for resolution

from __future__ import annotations
from src.logic.syntax import Formula, Atom, And, Not
from src.logic.cnf import to_cnf
from src.logic.resolution import entails


class BeliefBase:
    """A prioritised belief base for propositional formulas.

    Each belief is a ``(formula, priority)`` pair where *priority* acts as
    the epistemic entrenchment degree — higher priority means the belief is
    harder to retract during contraction.
    """

    def __init__(self):
        self._beliefs: list[tuple[Formula, float]] = []

    # ------------------------------------------------------------------
    # Basic operations
    # ------------------------------------------------------------------

    def add(self, formula: Formula, priority: float = 1.0) -> None:
        """Expansion: add *formula* with the given *priority*.

        If the formula already exists, update its priority to the new value.
        """
        for i, (f, _) in enumerate(self._beliefs):
            if f == formula:
                self._beliefs[i] = (formula, priority)
                return
        self._beliefs.append((formula, priority))

    def remove(self, formula: Formula) -> None:
        """Remove a specific formula from the belief base (by equality)."""
        self._beliefs = [(f, p) for f, p in self._beliefs if f != formula]

    def clear(self) -> None:
        """Remove all beliefs."""
        self._beliefs.clear()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_formulas(self) -> list[Formula]:
        """Return all formulas (without priorities)."""
        return [f for f, _ in self._beliefs]

    def get_beliefs(self) -> list[tuple[Formula, float]]:
        """Return all ``(formula, priority)`` pairs."""
        return list(self._beliefs)

    def __len__(self) -> int:
        return len(self._beliefs)

    def __contains__(self, formula: Formula) -> bool:
        return any(f == formula for f, _ in self._beliefs)

    def __iter__(self):
        return iter(self._beliefs)

    def __repr__(self) -> str:
        entries = ", ".join(f"({f}, {p})" for f, p in self._beliefs)
        return f"BeliefBase([{entries}])"

    # ------------------------------------------------------------------
    # Logical operations
    # ------------------------------------------------------------------

    def to_cnf_clauses(self) -> set[frozenset[str]]:
        """Convert the conjunction of all beliefs to a single CNF clause-set."""
        clauses: set[frozenset[str]] = set()
        for formula, _ in self._beliefs:
            clauses |= to_cnf(formula)
        return clauses

    def entails(self, formula: Formula) -> bool:
        """Does the belief base entail *formula*?

        This delegates to the resolution engine: ``KB ⊨ φ``.
        """
        if not self._beliefs:
            return False
        return entails(self.to_cnf_clauses(), formula)

    def is_consistent(self) -> bool:
        """Is the belief base consistent (non-contradictory)?

        A base is inconsistent iff it entails both ``p`` and ``¬p`` for some
        atom — equivalently, iff the CNF clause-set contains the empty clause
        after resolution.  We test by checking whether the base entails a
        known contradiction (``p ∧ ¬p`` for a dummy atom).
        """
        if not self._beliefs:
            return True

        # Collect all atoms used in the belief base
        all_atoms: set[str] = set()
        for formula, _ in self._beliefs:
            all_atoms |= formula.atoms()

        if not all_atoms:
            return True

        # A consistent base cannot entail any atom AND its negation
        # Pick any atom and check: a faster heuristic is to just check
        # if resolution on the full clause set ever produces empty clause
        clauses = self.to_cnf_clauses()
        # Check if empty clause is already present
        if frozenset() in clauses:
            return False

        # Check if we can derive a contradiction for any atom
        for atom_name in all_atoms:
            atom = Atom(atom_name)
            if entails(clauses, atom) and entails(clauses, Not(atom)):
                return False

        return True

    # ------------------------------------------------------------------
    # Copy
    # ------------------------------------------------------------------

    def copy(self) -> BeliefBase:
        """Return a shallow copy of this belief base."""
        new_bb = BeliefBase()
        new_bb._beliefs = list(self._beliefs)
        return new_bb
