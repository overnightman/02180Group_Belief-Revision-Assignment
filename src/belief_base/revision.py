# revision.py — AGM belief revision via the Levi identity
#
# Implements the AGM revision operator (*):
#
#   B * φ  =  (B ÷ ¬φ) + φ
#
# The Levi identity defines revision as:
#   1. First CONTRACT by ¬φ  (remove anything that would contradict φ)
#   2. Then EXPAND with φ     (add the new belief)
#
# This ensures the revised belief base is consistent (if φ is consistent)
# and contains φ (Success postulate).
#
# AGM revision postulates satisfied:
#   (*1) Closure, (*2) Success, (*3) Inclusion, (*4) Vacuity,
#   (*5) Consistency, (*6) Extensionality

from __future__ import annotations
from src.logic.syntax import Formula, Not
from src.belief_base.contraction import contract


def revise(belief_base, formula: Formula, priority: float = 1.0):
    """AGM revision via the Levi identity: ``B * φ = (B ÷ ¬φ) + φ``.

    Parameters
    ----------
    belief_base : BeliefBase
        The current belief base.
    formula : Formula
        The new formula to revise with.
    priority : float
        The priority (entrenchment) to assign to *formula*.

    Returns
    -------
    BeliefBase
        A new, revised belief base containing *formula*.
    """
    # Step 1: Contract by ¬φ  (remove beliefs contradicting φ)
    neg_formula = Not(formula)
    contracted = contract(belief_base, neg_formula)

    # Step 2: Expand with φ
    contracted.add(formula, priority)

    return contracted
