# Linear Program Conventions

Whenever asked to construct a linear program, unless otherwise stated, the linear
program should be in **standard equality form (SEF)**:

- the objective is a **maximization**,
- every constraint is an **equality** ($Ax = b$),
- every variable is **nonnegative** ($x \ge 0$).

When a request explicitly asks for a different form (for example, an LP "not in
SEF", or an LP with inequality constraints, or an LP to be converted into SEF),
follow that request instead.

## Canonical form / RREF row order

A matrix is only in **reduced row echelon form (RREF)** / canonical form with
respect to a basis if the basis columns form an identity matrix in **sorted
basis order**. That is, if the basis is $\{\beta_1 < \beta_2 < \dots < \beta_m\}$,
then column $\beta_1$ must have its leading $1$ in row $1$, column $\beta_2$ in
row $2$, and so on down the diagonal.

When writing out a canonical-form tableau (or doing row reduction), order the
rows so that the basis columns' $1$'s go **down the diagonal in sorted order**.
Do not leave the rows swapped. Label the basis set in sorted order to match.
