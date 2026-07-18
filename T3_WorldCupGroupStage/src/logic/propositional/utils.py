"""
utils.py

Utilities: pretty-print formulas, truth-table visualization,
and helpers for the workshop.
"""

from __future__ import annotations

from collections.abc import Sequence

from src.logic.propositional.ast import (
    And,
    Atom,
    Formula,
    Iff,
    Implies,
    Not,
    Or,
)


def formula_to_string(formula: Formula) -> str:
    """
    Convert a formula to readable infix notation.

    Example:
        >>> formula_to_string(Implies(Atom('p'), Not(Atom('q'))))
        '(p → ¬q)'
    """
    if isinstance(formula, Atom):
        return formula.name

    if isinstance(formula, Not):
        inner = formula_to_string(formula.operand)
        return f"¬{inner}"

    if isinstance(formula, And):
        parts = " ∧ ".join(formula_to_string(c) for c in formula.conjuncts)
        return f"({parts})"

    if isinstance(formula, Or):
        parts = " ∨ ".join(formula_to_string(d) for d in formula.disjuncts)
        return f"({parts})"

    if isinstance(formula, Implies):
        ant = formula_to_string(formula.antecedent)
        con = formula_to_string(formula.consequent)
        return f"({ant} → {con})"

    if isinstance(formula, Iff):
        left = formula_to_string(formula.left)
        right = formula_to_string(formula.right)
        return f"({left} ↔ {right})"

    return repr(formula)


def print_truth_table(
    headers: Sequence[str],
    rows: Sequence[Sequence[bool]],
) -> None:
    """
    Pretty-print a precomputed truth table as a markdown-style pipe table.

    You build the table yourself (with `get_atoms` / `evaluate` or
    `truth_table`); this function only formats and prints it.

    Args:
        headers: Column names (atom names + formula string).
        rows: Each row is a sequence of bools with the same length as
            ``headers`` (atom truth values + formula result).

    Example:
        >>> headers = ["p", "q", "(p → q)"]
        >>> rows = [
        ...     [True, True, True],
        ...     [True, False, False],
        ...     [False, True, True],
        ...     [False, False, True],
        ... ]
        >>> print_truth_table(headers, rows)
        | p     | q     | (p → q) |
        |-------|-------|---------|
        | True  | True  | True    |
        | True  | False | False   |
        | False | True  | True    |
        | False | False | True    |
    """
    if not headers:
        raise ValueError("headers must not be empty")

    col_widths = [
        max(len(h), 5, *(len(str(row[i])) for row in rows))
        for i, h in enumerate(headers)
    ]

    header = "|" + "|".join(f" {h:<{w}} " for h, w in zip(headers, col_widths)) + "|"
    separator = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"

    print(header)
    print(separator)

    for row in rows:
        if len(row) != len(headers):
            raise ValueError(
                f"row length {len(row)} does not match headers length {len(headers)}"
            )
        cells = "|" + "|".join(
            f" {str(val):<{w}} " for val, w in zip(row, col_widths)
        ) + "|"
        print(cells)


def format_model(model: dict[str, bool]) -> str:
    """
    Format a model in a readable way.

    Example:
        >>> format_model({'p': True, 'q': False, 'r': True})
        '{p = V, q = F, r = V}'
    """
    parts = []
    for atom in sorted(model.keys()):
        val = "V" if model[atom] else "F"
        parts.append(f"{atom} = {val}")
    return "{" + ", ".join(parts) + "}"


def format_kb(formulas: list[Formula]) -> str:
    """
    Format a knowledge base as a numbered list.

    Example:
        >>> format_kb([Atom('p'), Implies(Atom('p'), Atom('q'))])
        '1. p\\n2. (p → q)'
    """
    lines = []
    for i, f in enumerate(formulas, 1):
        lines.append(f"{i}. {formula_to_string(f)}")
    return "\n".join(lines)
