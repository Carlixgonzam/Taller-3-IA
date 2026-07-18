"""
ast.py

Defines the AST (Abstract Syntax Tree) for propositional formulas.
This is the backbone of the entire workshop.

Main classes:
    Formula, Atom, Not, And, Or, Implies, Iff

Main functions:
    get_atoms(formula) — extract all atomic propositions
    evaluate(formula, model) — evaluate a formula under a model
"""

from __future__ import annotations

from typing import FrozenSet


class Formula:
    """Abstract base class for all logical formulas."""

    def evaluate(self, model: dict[str, bool]) -> bool:
        raise NotImplementedError

    def get_atoms(self) -> FrozenSet[str]:
        raise NotImplementedError


class Atom(Formula):
    """
    Atomic proposition.

    Example:
        >>> Atom('suspect_in_kitchen')
        Atom('suspect_in_kitchen')
    """

    def __init__(self, name: str):
        self.name = name

    def evaluate(self, model: dict[str, bool]) -> bool:
        if self.name not in model:
            raise ValueError(
                f"Atom '{self.name}' has no value in the model. "
                f"Available atoms: {sorted(model.keys())}"
            )
        return model[self.name]

    def get_atoms(self) -> FrozenSet[str]:
        return frozenset({self.name})

    def __repr__(self) -> str:
        return f"Atom('{self.name}')"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Atom) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("Atom", self.name))


class Not(Formula):
    """
    Negation.

    Example:
        >>> Not(Atom('rained'))
        Not(Atom('rained'))
    """

    def __init__(self, operand: Formula):
        self.operand = operand

    def evaluate(self, model: dict[str, bool]) -> bool:
        return not self.operand.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.operand.get_atoms()

    def __repr__(self) -> str:
        return f"Not({self.operand!r})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Not) and self.operand == other.operand

    def __hash__(self) -> int:
        return hash(("Not", self.operand))


class And(Formula):
    """
    Conjunction (n-ary).

    Example:
        >>> And(Atom('p'), Atom('q'))
        And(Atom('p'), Atom('q'))
    """

    def __init__(self, *conjuncts: Formula):
        if len(conjuncts) < 2:
            raise ValueError("And requires at least 2 operands")
        self.conjuncts = tuple(conjuncts)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return all(c.evaluate(model) for c in self.conjuncts)

    def get_atoms(self) -> FrozenSet[str]:
        result: FrozenSet[str] = frozenset()
        for c in self.conjuncts:
            result = result | c.get_atoms()
        return result

    def __repr__(self) -> str:
        args = ", ".join(repr(c) for c in self.conjuncts)
        return f"And({args})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, And) and self.conjuncts == other.conjuncts

    def __hash__(self) -> int:
        return hash(("And", self.conjuncts))


class Or(Formula):
    """
    Disjunction (n-ary).

    Example:
        >>> Or(Atom('p'), Atom('q'))
        Or(Atom('p'), Atom('q'))
    """

    def __init__(self, *disjuncts: Formula):
        if len(disjuncts) < 2:
            raise ValueError("Or requires at least 2 operands")
        self.disjuncts = tuple(disjuncts)

    def evaluate(self, model: dict[str, bool]) -> bool:
        return any(d.evaluate(model) for d in self.disjuncts)

    def get_atoms(self) -> FrozenSet[str]:
        result: FrozenSet[str] = frozenset()
        for d in self.disjuncts:
            result = result | d.get_atoms()
        return result

    def __repr__(self) -> str:
        args = ", ".join(repr(d) for d in self.disjuncts)
        return f"Or({args})"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Or) and self.disjuncts == other.disjuncts

    def __hash__(self) -> int:
        return hash(("Or", self.disjuncts))


class Implies(Formula):
    """
    Implication.

    Example:
        >>> Implies(Atom('p'), Atom('q'))
        Implies(Atom('p'), Atom('q'))
    """

    def __init__(self, antecedent: Formula, consequent: Formula):
        self.antecedent = antecedent
        self.consequent = consequent

    def evaluate(self, model: dict[str, bool]) -> bool:
        return (not self.antecedent.evaluate(model)) or self.consequent.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.antecedent.get_atoms() | self.consequent.get_atoms()

    def __repr__(self) -> str:
        return f"Implies({self.antecedent!r}, {self.consequent!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Implies)
            and self.antecedent == other.antecedent
            and self.consequent == other.consequent
        )

    def __hash__(self) -> int:
        return hash(("Implies", self.antecedent, self.consequent))


class Iff(Formula):
    """
    Biconditional.

    Example:
        >>> Iff(Atom('p'), Atom('q'))
        Iff(Atom('p'), Atom('q'))
    """

    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    def evaluate(self, model: dict[str, bool]) -> bool:
        return self.left.evaluate(model) == self.right.evaluate(model)

    def get_atoms(self) -> FrozenSet[str]:
        return self.left.get_atoms() | self.right.get_atoms()

    def __repr__(self) -> str:
        return f"Iff({self.left!r}, {self.right!r})"

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Iff)
            and self.left == other.left
            and self.right == other.right
        )

    def __hash__(self) -> int:
        return hash(("Iff", self.left, self.right))


# ─── Utility functions ───────────────────────────────────────────────


def get_atoms(formula: Formula) -> frozenset[str]:
    """
    Extract all atomic propositions from a formula.

    Example:
        >>> get_atoms(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        frozenset({'p', 'q', 'r'})
    """
    return formula.get_atoms()


def evaluate(formula: Formula, model: dict[str, bool]) -> bool:
    """
    Evaluate a formula under a model (dict {str: bool}).

    Example:
        >>> evaluate(And(Atom('p'), Atom('q')), {'p': True, 'q': False})
        False
    """
    return formula.evaluate(model)
