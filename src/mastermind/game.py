# game.py — Mastermind game engine
#
# Implements the traditional Mastermind game logic:
#   - Secret code generation (4 pegs, 6 colours)
#   - Feedback computation: (black pegs = correct colour + position,
#                            white pegs = correct colour, wrong position)
#   - Game loop: guess → feedback → repeat until solved or max guesses
#
# This module is game-logic only; the AI code-breaker lives in agent.py.

from __future__ import annotations
import random


# Default colour palette (6 colours, numbered 0–5)
COLOURS = list(range(6))
CODE_LENGTH = 4
MAX_GUESSES = 10


class MastermindGame:
    """Mastermind game engine.

    Parameters
    ----------
    code_length : int
        Number of pegs in the secret code (default 4).
    num_colours : int
        Number of available colours (default 6).
    secret : list[int] | None
        Optional fixed secret code for testing.  If ``None``, a random code
        is generated.
    """

    def __init__(
        self,
        code_length: int = CODE_LENGTH,
        num_colours: int = len(COLOURS),
        secret: list[int] | None = None,
    ):
        self.code_length = code_length
        self.num_colours = num_colours
        self.colours = list(range(num_colours))

        if secret is not None:
            if len(secret) != code_length:
                raise ValueError(
                    f"Secret must have {code_length} pegs, got {len(secret)}"
                )
            self.secret = list(secret)
        else:
            self.secret = [random.choice(self.colours) for _ in range(code_length)]

        self.guesses: list[tuple[list[int], tuple[int, int]]] = []

    def get_feedback(self, guess: list[int]) -> tuple[int, int]:
        """Compute feedback for a guess.

        Returns
        -------
        (black, white) : tuple[int, int]
            - **black** = number of pegs with correct colour AND position
            - **white** = number of pegs with correct colour but WRONG position
        """
        if len(guess) != self.code_length:
            raise ValueError(
                f"Guess must have {self.code_length} pegs, got {len(guess)}"
            )

        black = sum(g == s for g, s in zip(guess, self.secret))

        # Count colour matches (min of occurrences in guess vs secret)
        total_colour_matches = 0
        for colour in self.colours:
            total_colour_matches += min(
                guess.count(colour), self.secret.count(colour)
            )

        white = total_colour_matches - black

        feedback = (black, white)
        self.guesses.append((list(guess), feedback))
        return feedback

    def is_solved(self, guess: list[int]) -> bool:
        """Return ``True`` if *guess* matches the secret code."""
        return guess == self.secret

    def play(self, agent) -> bool:
        """Run a full game with the given *agent*.

        The agent must implement:
          - ``make_guess() -> list[int]``
          - ``receive_feedback(guess, black, white)``

        Returns ``True`` if the agent cracks the code within ``MAX_GUESSES``.
        """
        for turn in range(1, MAX_GUESSES + 1):
            guess = agent.make_guess()
            if self.is_solved(guess):
                return True
            black, white = self.get_feedback(guess)
            agent.receive_feedback(guess, black, white)
        return False
