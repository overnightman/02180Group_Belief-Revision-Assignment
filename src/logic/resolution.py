# resolution.py — Resolution-based logical entailment
#
# Implements the resolution refutation procedure:
#   To check  KB ⊨ φ  (KB entails φ):
#     1. Convert KB ∧ ¬φ to CNF (set of clauses)
#     2. Repeatedly resolve pairs of clauses
#     3. If the empty clause □ is derived → KB ⊨ φ
#     4. If no new clauses can be derived → KB ⊭ φ
#
# This module is implemented from scratch (no SAT solver libraries),
# as required by the assignment.

from __future__ import annotations
from src.logic.syntax import Formula, Not
from src.logic.cnf import to_cnf


# ---------------------------------------------------------------------------
# Clause resolution
# ---------------------------------------------------------------------------

def resolve(clause1: frozenset[str], clause2: frozenset[str]) -> set[frozenset[str]]:
    """Resolve two clauses, returning all possible resolvents.

    For each complementary pair of literals (e.g. ``"p"`` and ``"~p"``),
    produce the resolvent = (clause1 ∪ clause2) minus the two literals.

    Returns an empty set if no complementary pair exists.
    A resolvent that is the empty frozenset represents the empty clause □.
    """
    resolvents: set[frozenset[str]] = set()

    for literal in clause1:
        # Find the complementary literal
        if literal.startswith("~"):
            complement = literal[1:]
        else:
            complement = f"~{literal}"

        if complement in clause2:
            # Build resolvent: merge both clauses, remove the pair
            new_clause = (clause1 - {literal}) | (clause2 - {complement})

            # Tautology filter: skip if clause contains both p and ~p
            if not _is_tautology(new_clause):
                resolvents.add(new_clause)

    return resolvents


def _is_tautology(clause: frozenset[str]) -> bool:
    """Return True if the clause contains both a literal and its negation."""
    for literal in clause:
        if literal.startswith("~"):
            if literal[1:] in clause:
                return True
        else:
            if f"~{literal}" in clause:
                return True
    return False


# ---------------------------------------------------------------------------
# Entailment via resolution refutation
# ---------------------------------------------------------------------------

def entails(kb_clauses: set[frozenset[str]], query: Formula) -> bool:
    """Check whether a knowledge base (in CNF) entails a query formula.

    Uses **resolution refutation**: KB ⊨ φ  iff  KB ∧ ¬φ is unsatisfiable.

    Parameters
    ----------
    kb_clauses : set[frozenset[str]]
        The knowledge base, already converted to a set of CNF clauses.
    query : Formula
        The formula to check entailment for.

    Returns
    -------
    bool
        ``True`` if the KB entails the query, ``False`` otherwise.
    """
    # Negate the query and convert to CNF
    negated_query_clauses = to_cnf(Not(query))

    # Combine KB ∧ ¬φ
    clauses = kb_clauses | negated_query_clauses

    # Resolution loop
    new: set[frozenset[str]] = set()

    while True:
        clause_list = list(clauses)
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = resolve(clause_list[i], clause_list[j])
                # If the empty clause is derived, entailment holds
                if frozenset() in resolvents:
                    return True
                new |= resolvents

        # If no new clauses were generated, entailment fails
        if new.issubset(clauses):
            return False

        clauses |= new


def entails_from_formulas(kb_formulas: list[Formula], query: Formula) -> bool:
    """Convenience wrapper: convert a list of formulas to CNF, then check entailment.

    Parameters
    ----------
    kb_formulas : list[Formula]
        The knowledge base as a list of Formula objects.
    query : Formula
        The formula to check entailment for.

    Returns
    -------
    bool
        ``True`` if the KB entails the query.
    """
    kb_clauses: set[frozenset[str]] = set()
    for f in kb_formulas:
        kb_clauses |= to_cnf(f)
    return entails(kb_clauses, query)
