"""Rough sets for incomplete information systems (Kryszkiewicz 1998).

The tolerance relation SIM(B): x and y are tolerant if, for each attribute a in B, a(x) = a(y),
or a(x) is missing, or a(y) is missing. The tolerance class I_B(x) is the set of all y with SIM(x, y).

A set of records is a bit set: a row of uint64 words, bit y is 1 if record y is in the set.
The tolerance classes of n records are an n x ceil(n / 64) matrix of words.
"""
import numpy as np
import pandas as pd

from src.data import numeric_attributes

# Memory limit for one block of rows of the tolerance matrix (number of uint64 words).
BLOCK_WORDS = 20_000_000


def cut_points(df: pd.DataFrame, bins: int = 4) -> dict[str, np.ndarray]:
    """Return the inner cut points of an equal-frequency discretization for each numeric attribute.

    The cut points come from the known values only. Equal values make some quantiles equal, so an attribute can
    have fewer than bins intervals.
    """
    cuts = {}
    for column in numeric_attributes(df):
        q = np.nanquantile(df[column].to_numpy(dtype=float), np.linspace(0, 1, bins + 1)[1:-1])
        cuts[column] = np.unique(q)
    return cuts


def discretize(df: pd.DataFrame, cuts: dict[str, np.ndarray]) -> pd.DataFrame:
    """Replace each numeric attribute with the number of its interval. A missing value stays missing.

    The cut points are a parameter, so the cut points of the training records also apply to the test records.
    """
    out = df.copy()
    for column, c in cuts.items():
        x = df[column].to_numpy(dtype=float)
        interval = np.searchsorted(c, x, side="right").astype(float)
        interval[np.isnan(x)] = np.nan
        out[column] = pd.Categorical(interval, categories=np.arange(len(c) + 1, dtype=float))
    return out


def encode(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list]:
    """Return the attribute codes (records x attributes, -1 if missing), the decision codes and the decision names.

    All attributes must be symbolic, so discretize the numeric attributes first.
    """
    attributes = df.columns.drop("class")
    assert not numeric_attributes(df), "discretize the numeric attributes first"
    codes = np.stack([df[c].cat.codes.to_numpy() for c in attributes], axis=1).astype(np.int32)
    return codes, df["class"].cat.codes.to_numpy().astype(np.int32), list(df["class"].cat.categories)


def pack(members: np.ndarray) -> np.ndarray:
    """Make bit sets from a boolean array (... x n). Return an array (... x ceil(n / 64)) of uint64."""
    n = members.shape[-1]
    padded = np.zeros(members.shape[:-1] + (-(-n // 64) * 64,), dtype=bool)
    padded[..., :n] = members
    return np.packbits(padded, axis=-1, bitorder="little").view(np.uint64)


def unpack(bits: np.ndarray, n: int) -> np.ndarray:
    """Make a boolean array (... x n) from bit sets."""
    return np.unpackbits(bits.view(np.uint8), axis=-1, bitorder="little")[..., :n].astype(bool)


def count(bits: np.ndarray) -> np.ndarray:
    """Return the number of records in each bit set."""
    return np.bitwise_count(bits).sum(axis=-1, dtype=np.int64)


def tolerance_classes(codes: np.ndarray, attributes=None) -> np.ndarray:
    """Return the tolerance classes I_B(x) of all records for the attributes B (default: all attributes).

    For each attribute a and each value v, the bit set S(a, v) has the records with a = v or a missing.
    Then I_B(x) is the AND of S(a, a(x)) for a in B, with a skipped if a(x) is missing.
    The time is O(|B| * n * n / 64) word operations, the memory is n * n / 8 bytes.
    """
    n, m = codes.shape
    attributes = range(m) if attributes is None else attributes
    words = -(-n // 64)
    tolerant = []
    for a in attributes:
        column = codes[:, a]
        values = np.arange(-1, column.max() + 1)
        # Row 0 (a missing in x) is the full set, row v + 1 is S(a, v).
        members = (column[None, :] == values[:, None]) | (column[None, :] == -1)
        members[0] = True
        tolerant.append((a, pack(members)))
    classes = np.full((n, words), np.iinfo(np.uint64).max, dtype=np.uint64)
    block = max(1, BLOCK_WORDS // words)
    for start in range(0, n, block):
        rows = slice(start, start + block)
        for a, bits in tolerant:
            classes[rows] &= bits[codes[rows, a] + 1]
    # Clear the padding bits after the last record.
    classes &= pack(np.ones(n, dtype=bool))
    return classes


def lower_approximation(classes: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Return the records x with I(x) in the target set (a bit set). The result is a boolean array."""
    return ~np.any(classes & ~target, axis=1)


def upper_approximation(classes: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Return the records x with I(x) and the target set not disjoint. The result is a boolean array."""
    return np.any(classes & target, axis=1)


def generalized_decision(classes: np.ndarray, decision: np.ndarray) -> np.ndarray:
    """Return the generalized decision of each record: the set of the decisions in I(x).

    The result is a boolean array (records x decisions).
    """
    per_decision = pack(decision[None, :] == np.arange(decision.max() + 1)[:, None])
    return np.stack([upper_approximation(classes, d) for d in per_decision], axis=1)
