# syntax.py — Propositional logic formula representation
#
# Defines the AST (Abstract Syntax Tree) for propositional formulas:
#   - Atom(name)          : propositional variable, e.g. "p", "q"
#   - Not(formula)        : negation  ¬φ
#   - And(left, right)    : conjunction  φ ∧ ψ
#   - Or(left, right)     : disjunction  φ ∨ ψ
#   - Implies(left, right): implication  φ → ψ
#   - Biconditional(l, r) : biconditional  φ ↔ ψ
#
# Also provides a parser to convert string representations into AST nodes.

from __future__ import annotations


# ---------------------------------------------------------------------------
# AST node classes
# ---------------------------------------------------------------------------

class Formula:
    """Abstract base class for all propositional formulas."""

    def atoms(self) -> set[str]:
        """Return the set of all propositional variable names in this formula."""
        raise NotImplementedError

    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self):
        raise NotImplementedError


class Atom(Formula):
    """A propositional variable, e.g. 'p', 'q', 'rain'."""

    def __init__(self, name: str):
        self.name = name

    def atoms(self) -> set[str]:
        return {self.name}

    def __eq__(self, other):
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self):
        return hash(("Atom", self.name))

    def __repr__(self):
        return f"Atom({self.name!r})"

    def __str__(self):
        return self.name


class Not(Formula):
    """Negation: ¬φ."""

    def __init__(self, operand: Formula):
        self.operand = operand

    def atoms(self) -> set[str]:
        return self.operand.atoms()

    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self):
        return hash(("Not", self.operand))

    def __repr__(self):
        return f"Not({self.operand!r})"

    def __str__(self):
        # Parenthesise compound operands for clarity
        if isinstance(self.operand, Atom):
            return f"~{self.operand}"
        return f"~({self.operand})"


class And(Formula):
    """Conjunction: φ ∧ ψ."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def atoms(self) -> set[str]:
        return self.left.atoms() | self.right.atoms()

    def __eq__(self, other):
        return isinstance(other, And) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("And", self.left, self.right))

    def __repr__(self):
        return f"And({self.left!r}, {self.right!r})"

    def __str__(self):
        left = self._wrap(self.left)
        right = self._wrap(self.right)
        return f"{left} & {right}"

    @staticmethod
    def _wrap(f: Formula) -> str:
        if isinstance(f, (Or, Implies, Biconditional)):
            return f"({f})"
        return str(f)


class Or(Formula):
    """Disjunction: φ ∨ ψ."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def atoms(self) -> set[str]:
        return self.left.atoms() | self.right.atoms()

    def __eq__(self, other):
        return isinstance(other, Or) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("Or", self.left, self.right))

    def __repr__(self):
        return f"Or({self.left!r}, {self.right!r})"

    def __str__(self):
        left = self._wrap(self.left)
        right = self._wrap(self.right)
        return f"{left} | {right}"

    @staticmethod
    def _wrap(f: Formula) -> str:
        if isinstance(f, (Implies, Biconditional)):
            return f"({f})"
        return str(f)


class Implies(Formula):
    """Implication: φ → ψ."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def atoms(self) -> set[str]:
        return self.left.atoms() | self.right.atoms()

    def __eq__(self, other):
        return isinstance(other, Implies) and self.left == other.left and self.right == other.right

    def __hash__(self):
        return hash(("Implies", self.left, self.right))

    def __repr__(self):
        return f"Implies({self.left!r}, {self.right!r})"

    def __str__(self):
        left = self._wrap(self.left)
        right = str(self.right)
        return f"{left} -> {right}"

    @staticmethod
    def _wrap(f: Formula) -> str:
        if isinstance(f, (Implies, Biconditional)):
            return f"({f})"
        return str(f)


class Biconditional(Formula):
    """Biconditional: φ ↔ ψ."""

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def atoms(self) -> set[str]:
        return self.left.atoms() | self.right.atoms()

    def __eq__(self, other):
        return (isinstance(other, Biconditional)
                and self.left == other.left and self.right == other.right)

    def __hash__(self):
        return hash(("Biconditional", self.left, self.right))

    def __repr__(self):
        return f"Biconditional({self.left!r}, {self.right!r})"

    def __str__(self):
        return f"{self.left} <-> {self.right}"


# ---------------------------------------------------------------------------
# Tokeniser
# ---------------------------------------------------------------------------

_TOKEN_MAP = {
    "~": "NOT",
    "&": "AND",
    "|": "OR",
    "(": "LPAREN",
    ")": "RPAREN",
}


def _tokenise(text: str) -> list[tuple[str, str]]:
    """Convert a formula string into a list of (token_type, value) pairs."""
    tokens: list[tuple[str, str]] = []
    i = 0
    while i < len(text):
        ch = text[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Two-character operators
        if text[i:i+3] == "<->":
            tokens.append(("BICOND", "<->"))
            i += 3
            continue
        if text[i:i+2] == "->":
            tokens.append(("IMPLIES", "->"))
            i += 2
            continue

        # Single-character operators / parens
        if ch in _TOKEN_MAP:
            tokens.append((_TOKEN_MAP[ch], ch))
            i += 1
            continue

        # Atom names: letters, digits, underscores (must start with letter/underscore)
        if ch.isalpha() or ch == "_":
            start = i
            while i < len(text) and (text[i].isalnum() or text[i] == "_"):
                i += 1
            tokens.append(("ATOM", text[start:i]))
            continue

        raise ValueError(f"Unexpected character {ch!r} at position {i}")

    tokens.append(("EOF", ""))
    return tokens


# ---------------------------------------------------------------------------
# Recursive-descent parser
# ---------------------------------------------------------------------------
# Precedence (low → high):
#   biconditional  <->
#   implication    ->   (right-associative)
#   disjunction    |
#   conjunction    &
#   negation       ~
#   atom / parens

class _Parser:
    """Recursive-descent parser for propositional formulas."""

    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0

    def _peek(self) -> tuple[str, str]:
        return self.tokens[self.pos]

    def _consume(self, expected_type: str | None = None) -> tuple[str, str]:
        token = self.tokens[self.pos]
        if expected_type and token[0] != expected_type:
            raise ValueError(
                f"Expected {expected_type} but got {token[0]} ({token[1]!r})"
            )
        self.pos += 1
        return token

    # --- Grammar rules ---

    def parse(self) -> Formula:
        result = self._biconditional()
        if self._peek()[0] != "EOF":
            raise ValueError(
                f"Unexpected token {self._peek()[1]!r} after complete formula"
            )
        return result

    def _biconditional(self) -> Formula:
        left = self._implication()
        while self._peek()[0] == "BICOND":
            self._consume()
            right = self._implication()
            left = Biconditional(left, right)
        return left

    def _implication(self) -> Formula:
        left = self._disjunction()
        # Right-associative: a -> b -> c  =  a -> (b -> c)
        if self._peek()[0] == "IMPLIES":
            self._consume()
            right = self._implication()  # recurse for right-assoc
            return Implies(left, right)
        return left

    def _disjunction(self) -> Formula:
        left = self._conjunction()
        while self._peek()[0] == "OR":
            self._consume()
            right = self._conjunction()
            left = Or(left, right)
        return left

    def _conjunction(self) -> Formula:
        left = self._unary()
        while self._peek()[0] == "AND":
            self._consume()
            right = self._unary()
            left = And(left, right)
        return left

    def _unary(self) -> Formula:
        if self._peek()[0] == "NOT":
            self._consume()
            operand = self._unary()
            return Not(operand)
        return self._primary()

    def _primary(self) -> Formula:
        tok_type, tok_val = self._peek()
        if tok_type == "ATOM":
            self._consume()
            return Atom(tok_val)
        if tok_type == "LPAREN":
            self._consume()
            expr = self._biconditional()
            self._consume("RPAREN")
            return expr
        raise ValueError(f"Unexpected token {tok_val!r}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse(text: str) -> Formula:
    """Parse a propositional formula string into an AST.

    Supported syntax:
        atoms:   p, q, rain, my_var   (letters/digits/underscores)
        not:     ~p
        and:     p & q
        or:      p | q
        implies: p -> q
        bicond:  p <-> q
        parens:  (p | q) & r

    Precedence (low → high): <->, ->, |, &, ~
    """
    tokens = _tokenise(text)
    parser = _Parser(tokens)
    return parser.parse()
