# cnf.py — Conjunctive Normal Form conversion
#
# Converts an arbitrary propositional formula (AST) into CNF.
# Steps:
#   1. Eliminate biconditionals  (φ ↔ ψ) ≡ (φ → ψ) ∧ (ψ → φ)
#   2. Eliminate implications     (φ → ψ) ≡ (¬φ ∨ ψ)
#   3. Push negations inward     (De Morgan's laws, double negation elimination)
#   4. Distribute ∨ over ∧       to reach a conjunction of disjunctions
#
# The output is a set of clauses, where each clause is a frozenset of literals.

from __future__ import annotations
from src.logic.syntax import Formula, Atom, Not, And, Or, Implies, Biconditional


# ---------------------------------------------------------------------------
# Step 1: Eliminate biconditionals
# ---------------------------------------------------------------------------

def eliminate_biconditionals(formula: Formula) -> Formula:
    """Replace (φ ↔ ψ) with (φ → ψ) ∧ (ψ → φ), recursively."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_biconditionals(formula.operand))
    if isinstance(formula, And):
        return And(eliminate_biconditionals(formula.left),
                   eliminate_biconditionals(formula.right))
    if isinstance(formula, Or):
        return Or(eliminate_biconditionals(formula.left),
                  eliminate_biconditionals(formula.right))
    if isinstance(formula, Implies):
        return Implies(eliminate_biconditionals(formula.left),
                       eliminate_biconditionals(formula.right))
    if isinstance(formula, Biconditional):
        left = eliminate_biconditionals(formula.left)
        right = eliminate_biconditionals(formula.right)
        return And(Implies(left, right), Implies(right, left))
    raise TypeError(f"Unknown formula type: {type(formula)}")


# ---------------------------------------------------------------------------
# Step 2: Eliminate implications
# ---------------------------------------------------------------------------

def eliminate_implications(formula: Formula) -> Formula:
    """Replace (φ → ψ) with (¬φ ∨ ψ), recursively."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        return Not(eliminate_implications(formula.operand))
    if isinstance(formula, And):
        return And(eliminate_implications(formula.left),
                   eliminate_implications(formula.right))
    if isinstance(formula, Or):
        return Or(eliminate_implications(formula.left),
                  eliminate_implications(formula.right))
    if isinstance(formula, Implies):
        left = eliminate_implications(formula.left)
        right = eliminate_implications(formula.right)
        return Or(Not(left), right)
    if isinstance(formula, Biconditional):
        # Should have been eliminated already, but handle defensively
        return eliminate_implications(eliminate_biconditionals(formula))
    raise TypeError(f"Unknown formula type: {type(formula)}")


# ---------------------------------------------------------------------------
# Step 3: Push negations inward (NNF — Negation Normal Form)
# ---------------------------------------------------------------------------

def push_negations(formula: Formula) -> Formula:
    """Apply De Morgan's laws and double-negation elimination recursively."""
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, And):
        return And(push_negations(formula.left), push_negations(formula.right))
    if isinstance(formula, Or):
        return Or(push_negations(formula.left), push_negations(formula.right))
    if isinstance(formula, Not):
        inner = formula.operand
        # Double negation: ¬¬φ ≡ φ
        if isinstance(inner, Not):
            return push_negations(inner.operand)
        # De Morgan: ¬(φ ∧ ψ) ≡ ¬φ ∨ ¬ψ
        if isinstance(inner, And):
            return Or(push_negations(Not(inner.left)),
                      push_negations(Not(inner.right)))
        # De Morgan: ¬(φ ∨ ψ) ≡ ¬φ ∧ ¬ψ
        if isinstance(inner, Or):
            return And(push_negations(Not(inner.left)),
                       push_negations(Not(inner.right)))
        # ¬atom stays as-is
        if isinstance(inner, Atom):
            return formula
        # ¬(φ → ψ) or ¬(φ ↔ ψ) shouldn't appear after steps 1-2,
        # but handle defensively
        if isinstance(inner, Implies):
            # ¬(φ → ψ) ≡ φ ∧ ¬ψ
            return push_negations(And(inner.left, Not(inner.right)))
        if isinstance(inner, Biconditional):
            return push_negations(Not(eliminate_implications(
                eliminate_biconditionals(inner))))
    if isinstance(formula, (Implies, Biconditional)):
        # Should have been eliminated, but handle defensively
        return push_negations(eliminate_implications(
            eliminate_biconditionals(formula)))
    raise TypeError(f"Unknown formula type: {type(formula)}")


# ---------------------------------------------------------------------------
# Step 4: Distribute ∨ over ∧
# ---------------------------------------------------------------------------

def distribute_or_over_and(formula: Formula) -> Formula:
    """Convert NNF to CNF by distributing ∨ over ∧.

    (φ ∨ (ψ ∧ χ)) ≡ (φ ∨ ψ) ∧ (φ ∨ χ)
    ((ψ ∧ χ) ∨ φ) ≡ (ψ ∨ φ) ∧ (χ ∨ φ)
    """
    if isinstance(formula, Atom) or isinstance(formula, Not):
        return formula
    if isinstance(formula, And):
        return And(distribute_or_over_and(formula.left),
                   distribute_or_over_and(formula.right))
    if isinstance(formula, Or):
        left = distribute_or_over_and(formula.left)
        right = distribute_or_over_and(formula.right)
        return _distribute(left, right)
    raise TypeError(f"Unknown formula type: {type(formula)}")


def _distribute(left: Formula, right: Formula) -> Formula:
    """Distribute a disjunction over any conjunctions in its operands."""
    # (α ∧ β) ∨ γ  →  (α ∨ γ) ∧ (β ∨ γ)
    if isinstance(left, And):
        return And(_distribute(left.left, right),
                   _distribute(left.right, right))
    # α ∨ (β ∧ γ)  →  (α ∨ β) ∧ (α ∨ γ)
    if isinstance(right, And):
        return And(_distribute(left, right.left),
                   _distribute(left, right.right))
    return Or(left, right)


# ---------------------------------------------------------------------------
# Clause extraction
# ---------------------------------------------------------------------------

def _formula_to_clauses(formula: Formula) -> set[frozenset[str]]:
    """Extract clauses from a CNF formula (conjunction of disjunctions).

    Each clause is a frozenset of string literals, e.g. {"p", "~q"}.
    """
    if isinstance(formula, And):
        return _formula_to_clauses(formula.left) | _formula_to_clauses(formula.right)
    # A single clause (disjunction of literals, or a single literal)
    clause = _extract_literals(formula)
    return {clause}


def _extract_literals(formula: Formula) -> frozenset[str]:
    """Extract literals from a single clause (a disjunction of literals)."""
    if isinstance(formula, Atom):
        return frozenset({formula.name})
    if isinstance(formula, Not):
        if isinstance(formula.operand, Atom):
            return frozenset({f"~{formula.operand.name}"})
        raise ValueError(f"Expected a literal, got Not({formula.operand})")
    if isinstance(formula, Or):
        return _extract_literals(formula.left) | _extract_literals(formula.right)
    raise ValueError(f"Expected a literal or disjunction, got {type(formula).__name__}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def to_cnf(formula: Formula) -> set[frozenset[str]]:
    """Convert a propositional formula into CNF (set of clauses).

    Returns a set of clauses, where each clause is a frozenset of string
    literals.  Positive literals are like ``"p"``, negative like ``"~p"``.

    Example::

        >>> to_cnf(parse("p -> q"))
        {frozenset({'~p', 'q'})}
    """
    step1 = eliminate_biconditionals(formula)
    step2 = eliminate_implications(step1)
    step3 = push_negations(step2)
    step4 = distribute_or_over_and(step3)
    return _formula_to_clauses(step4)
