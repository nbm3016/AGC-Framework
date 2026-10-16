"""Casimir values on the wall-index line. Not a Dirac index."""

from fractions import Fraction


def casimir(j: Fraction) -> Fraction:
    """Six times the SU(2) Casimir j(j+1)."""
    return 6 * j * (j + 1)


def sieve(j: Fraction) -> int:
    """max(0, floor(4j-6)). Exact on these rationals."""
    raw = 4 * j - 6
    # raw is an integer for j in {1/2, 1, 3/2, 2}.
    floored = int(raw)
    return max(0, floored)


def main() -> None:
    zeros = []
    for label in (Fraction(1, 2), Fraction(1), Fraction(3, 2), Fraction(2)):
        value = casimir(label)
        index = sieve(label)
        print(f"j={label} lambda={value} sieve={index}")
        if index == 0 and label != 0:
            zeros.append(label)
    print(f"sieve zeros {zeros}")
    print("dirac index UNPERFORMED")


if __name__ == "__main__":
    main()
