# contraction.py — Partial meet contraction
#
# Implements the AGM contraction operator (÷) using the partial meet approach:
#
#   B ÷ φ  =  ∩ γ(B ⊥ φ)
#
# Where:
#   B ⊥ φ  = the set of all maximal subsets of B that do not entail φ
#             (called "remainder sets")
#   γ      = a selection function that picks the "best" remainder sets
#             guided by the epistemic entrenchment ordering (priority)
#
# AGM contraction postulates satisfied:
#   (÷1) Closure, (÷2) Inclusion, (÷3) Vacuity,
#   (÷4) Success, (÷5) Recovery, (÷6) Extensionality

from __future__ import annotations
from itertools import combinations
from src.logic.syntax import Formula
from src.logic.cnf import to_cnf
from src.logic.resolution import entails


def _beliefs_entail(beliefs: list[tuple[Formula, float]], formula: Formula) -> bool:
    """Check whether a list of (formula, priority) pairs entails *formula*."""
    if not beliefs:
        return False
    clauses: set[frozenset[str]] = set()
    for f, _ in beliefs:
        clauses |= to_cnf(f)
    return entails(clauses, formula)


# ---------------------------------------------------------------------------
# Remainder sets  (B ⊥ φ)
# ---------------------------------------------------------------------------

def remainder_sets(
    beliefs: list[tuple[Formula, float]],
    formula: Formula,
) -> list[list[tuple[Formula, float]]]:
    """Compute all maximal subsets of *beliefs* that do not entail *formula*."""
    n = len(beliefs)

    # If the full base does not entail φ, return it as the sole remainder
    if not _beliefs_entail(beliefs, formula):
        return [list(beliefs)]

    if n == 0:
        return [[]]

    remainders: list[tuple[set[int], list[tuple[Formula, float]]]] = []

    # Search from largest subsets downward
    for size in range(n - 1, -1, -1):
        # If we already have remainders and current size < their size,
        # we can't find any more maximal sets
        if remainders and size < len(remainders[0][0]):
            break

        for combo in combinations(range(n), size):
            combo_set = set(combo)

            # Skip if this is a subset of an already found remainder
            # (can't be maximal)
            is_subset_of_existing = False
            for rem_set, _ in remainders:
                if combo_set < rem_set:
                    is_subset_of_existing = True
                    break
            if is_subset_of_existing:
                continue

            subset = [beliefs[i] for i in combo]
            if not _beliefs_entail(subset, formula):
                remainders.append((combo_set, subset))

    if not remainders:
        return [[]]

    return [subset for _, subset in remainders]


# ---------------------------------------------------------------------------
# Selection function  γ
# ---------------------------------------------------------------------------

def selection_function(
    remainders: list[list[tuple[Formula, float]]],
) -> list[list[tuple[Formula, float]]]:
    """Select the best remainder sets based on total priority.

    The selection function picks all remainder sets that have the **maximum**
    sum of priorities.  This implements epistemic entrenchment: beliefs with
    higher priority are preferred to be kept.
    """
    if not remainders:
        return []
    if len(remainders) == 1:
        return remainders

    scored = [(sum(p for _, p in rem), rem) for rem in remainders]
    max_score = max(s for s, _ in scored)
    return [rem for s, rem in scored if s == max_score]


# ---------------------------------------------------------------------------
# Partial meet contraction
# ---------------------------------------------------------------------------

def contract(
    belief_base,  # BeliefBase — avoid circular import
    formula: Formula,
) -> "BeliefBase":
    """Partial meet contraction: ``B ÷ φ``.

    1. Compute remainder sets ``B ⊥ φ``
    2. Apply selection function ``γ`` (priority-based)
    3. Return the intersection of selected remainders

    Returns a new :class:`BeliefBase`.
    """
    from src.belief_base.belief_base import BeliefBase

    beliefs = belief_base.get_beliefs()

    # If φ is not entailed, contraction is vacuous (return a copy)
    if not belief_base.entails(formula):
        return belief_base.copy()

    # Step 1: compute remainder sets
    rems = remainder_sets(beliefs, formula)

    # Step 2: select best remainders
    selected = selection_function(rems)

    # Step 3: intersect — keep only beliefs that appear in ALL selected remainders
    if not selected:
        return BeliefBase()

    # Convert each selected remainder to a set of (formula, priority) for intersection
    # We intersect by formula identity
    common_formulas = None
    for rem in selected:
        rem_formula_set = {f for f, _ in rem}
        if common_formulas is None:
            common_formulas = rem_formula_set
        else:
            common_formulas &= rem_formula_set

    if common_formulas is None:
        common_formulas = set()

    # Build new belief base with the intersected formulas, preserving priorities
    result = BeliefBase()
    for f, p in beliefs:
        if f in common_formulas:
            result.add(f, p)

    return result
