"""
model_checking.py

This module contains propositional model-checking functions.

Hint: Use get_atoms() and evaluate() from ast.py.
"""

from __future__ import annotations

from src.logic.propositional.ast import And, Formula, Not, evaluate, get_atoms


def get_all_models(atoms: set[str]) -> list[dict[str, bool]]:
    """
    Generate all possible models (truth assignments).
    For n atoms, generates 2^n models.

    Args:
        atoms: Set of propositional atom names.

    Returns:
        List of dictionaries, each mapping atoms to boolean values.

    Example:
        >>> get_all_models({'p', 'q'})
        [{'p': True, 'q': True}, {'p': True, 'q': False},
         {'p': False, 'q': True}, {'p': False, 'q': False}]

    Hint: Think of numbers from 0 to 2^n - 1 in binary.
          Each bit corresponds to the truth value of an atom.
    """
    # === YOUR CODE HERE ===
    models = []
    n = len(atoms)
    list_atoms = list(atoms)
    for i in range(2 ** n):
        model = {}
        binary = bin(i)[2:].zfill(n)
        for j in range(n):
            model[list_atoms[j]] = True if binary[j] == '1' else False
        models.append(model)
    return models



    # === END YOUR CODE ===
    raise NotImplementedError("Implement get_all_models()")


def check_satisfiable(formula: Formula) -> tuple[bool, dict[str, bool] | None]:
    """
    Determine whether a formula is satisfiable.

    Args:
        formula: Logical formula to check.

    Returns:
        (True, model) if a satisfying model is found.
        (False, None) if unsatisfiable.

    Example:
        >>> check_satisfiable(And(Atom('p'), Not(Atom('p'))))
        (False, None)

    Hint: Generate all models with get_all_models(), then evaluate
          the formula on each using evaluate().
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement check_satisfiable()")


def check_valid(formula: Formula) -> bool:
    """
    Determine whether a formula is a tautology (valid in every model).

    Args:
        formula: Logical formula to check.

    Returns:
        True if the formula is true in all possible models.

    Example:
        >>> check_valid(Or(Atom('p'), Not(Atom('p'))))
        True

    Hint: A formula is valid iff its negation is unsatisfiable.
          Alternatively, check that it is true in ALL models.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement check_valid()")


def check_entailment(kb: list[Formula], query: Formula) -> bool:
    """
    Determine whether KB |= query (the knowledge base entails the query).

    Args:
        kb: List of formulas forming the knowledge base.
        query: Formula we want to check follows from the KB.

    Returns:
        True if the query is true in every model where the KB is true.

    Example:
        >>> kb = [Implies(Atom('p'), Atom('q')), Atom('p')]
        >>> check_entailment(kb, Atom('q'))
        True

    Hint: KB |= q  iff  KB ∧ ¬q is unsatisfiable.
          That is, there is no model where the whole KB is true
          and the query is false.
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement check_entailment()")


def truth_table(formula: Formula) -> list[tuple[dict[str, bool], bool]]:
    """
    Generate the full truth table of a formula.

    Args:
        formula: Logical formula.

    Returns:
        List of (model, result) tuples for every possible model.

    Example:
        >>> truth_table(And(Atom('p'), Atom('q')))
        [({'p': True, 'q': True}, True),
         ({'p': True, 'q': False}, False),
         ({'p': False, 'q': True}, False),
         ({'p': False, 'q': False}, False)]

    Hint: Combine get_all_models() and evaluate().
    """
    # === YOUR CODE HERE ===
    # === END YOUR CODE ===
    raise NotImplementedError("Implement truth_table()")
