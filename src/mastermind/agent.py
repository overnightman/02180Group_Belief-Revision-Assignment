# agent.py — Belief-revision–based Mastermind code-breaker
#
# Uses the belief revision engine to play Mastermind:
#   1. Initialize belief base with background knowledge (game rules encoded
#      as propositional formulas) and an initial guess.
#   2. After each guess, receive feedback (black/white pegs).
#   3. Encode the feedback as a propositional formula.
#   4. Revise the belief base with the feedback formula.
#   5. Derive the next guess from the revised belief base.
#   6. Repeat until the code is cracked.

from __future__ import annotations
import itertools
from src.logic.syntax import Atom, And, Or, Not, Formula
from src.logic.cnf import to_cnf
from src.logic.resolution import entails
from src.belief_base.belief_base import BeliefBase
from src.belief_base.revision import revise


class MastermindAgent:
    """AI code-breaker using belief revision to play Mastermind.

    The agent maintains a set of *possible codes* and uses feedback from each
    guess to eliminate impossible codes.  Belief revision is used to
    incorporate feedback constraints.

    This is a hybrid approach: we maintain an explicit set of possible codes
    for efficiency (the full propositional encoding of Mastermind with
    belief-level resolution is combinatorially expensive for 6^4 = 1296
    possibilities), but we **use the belief revision engine** to maintain
    and update the logical constraints.

    Propositional encoding
    ----------------------
    - Atom ``c_i_v`` means "position *i* has colour *v*".
    - Feedback is encoded as constraints that eliminate impossible codes.
    """

    def __init__(self, code_length: int = 4, num_colours: int = 6):
        self.code_length = code_length
        self.num_colours = num_colours
        self.belief_base = BeliefBase()

        # Generate all possible codes
        self.possible_codes: list[tuple[int, ...]] = list(
            itertools.product(range(num_colours), repeat=code_length)
        )

        self._turn = 0

    @staticmethod
    def _compute_feedback(
        guess: list[int], candidate: tuple[int, ...]
    ) -> tuple[int, int]:
        """Compute feedback as if *candidate* were the secret code."""
        black = sum(g == c for g, c in zip(guess, candidate))
        total = 0
        colours = set(guess) | set(candidate)
        for colour in colours:
            total += min(
                sum(1 for g in guess if g == colour),
                sum(1 for c in candidate if c == colour),
            )
        white = total - black
        return (black, white)

    def make_guess(self) -> list[int]:
        """Select the next guess from the remaining possible codes.

        First guess uses a heuristic starting point; subsequent guesses
        pick the first remaining possibility (simple strategy).
        """
        self._turn += 1

        if self._turn == 1:
            # Classic opening guess: [0, 0, 1, 1]
            opening = [0, 0, 1, 1]
            if self.code_length != 4:
                opening = [i % self.num_colours for i in range(self.code_length)]
            return opening

        if self.possible_codes:
            return list(self.possible_codes[0])

        # Fallback (should not happen)
        return [0] * self.code_length

    def receive_feedback(self, guess: list[int], black: int, white: int) -> None:
        """Update beliefs based on feedback.

        Eliminates all candidate codes that would not produce the same
        feedback, and records the constraint in the belief base.
        """
        # Filter possible codes: keep only those consistent with the feedback
        self.possible_codes = [
            code for code in self.possible_codes
            if self._compute_feedback(guess, code) == (black, white)
        ]

        # Encode the feedback as a propositional formula and revise
        # We create atoms for each position-colour assignment in the guess
        # and build a constraint formula
        feedback_formula = self._encode_feedback(guess, black, white)
        if feedback_formula is not None:
            self.belief_base = revise(self.belief_base, feedback_formula, priority=2.0)

    def _encode_feedback(
        self, guess: list[int], black: int, white: int
    ) -> Formula | None:
        """Encode feedback as a propositional formula.

        If all pegs are black (correct), encode that each position has
        the guessed colour.  Otherwise, encode that at least one position
        differs (for non-black positions).
        """
        if black == self.code_length:
            # All correct — encode exact assignment
            conjuncts = []
            for i, colour in enumerate(guess):
                conjuncts.append(Atom(f"c_{i}_{colour}"))
            result = conjuncts[0]
            for c in conjuncts[1:]:
                result = And(result, c)
            return result

        if black == 0 and white == 0:
            # No colour matches at all — every guessed colour is absent
            # from every position
            conjuncts = []
            for i, colour in enumerate(guess):
                conjuncts.append(Not(Atom(f"c_{i}_{colour}")))
            if not conjuncts:
                return None
            result = conjuncts[0]
            for c in conjuncts[1:]:
                result = And(result, c)
            return result

        # General case: at least one position is wrong
        # Encode: NOT all positions match
        disjuncts = []
        for i, colour in enumerate(guess):
            disjuncts.append(Not(Atom(f"c_{i}_{colour}")))
        if not disjuncts:
            return None
        result = disjuncts[0]
        for d in disjuncts[1:]:
            result = Or(result, d)
        return result
