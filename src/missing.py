"""Simulation of missing values: random removal of attribute values (MCAR)."""
import numpy as np
import pandas as pd


def add_mcar(df: pd.DataFrame, fraction: float, seed: int) -> tuple[pd.DataFrame, np.ndarray]:
    """Remove a fraction of the known attribute values at random. The class is never removed.

    Each known value has the same probability of removal, so the removal does not depend on the data (MCAR).
    Return the new table and a boolean mask (records x attributes) of the removed values.
    The mask gives the true values for the error of an imputation.
    """
    assert 0.0 <= fraction < 1.0
    attributes = [c for c in df.columns if c != "class"]
    known = df[attributes].notna().to_numpy()
    positions = np.flatnonzero(known)
    rng = np.random.default_rng(seed)
    chosen = rng.choice(positions, size=round(fraction * len(positions)), replace=False)
    removed = np.zeros(known.size, dtype=bool)
    removed[chosen] = True
    removed = removed.reshape(known.shape)
    out = df.copy()
    out[attributes] = out[attributes].mask(removed)
    return out, removed
