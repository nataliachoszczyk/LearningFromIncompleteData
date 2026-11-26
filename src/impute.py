"""Imputation of missing values: kNN (Troyanskaya et al. 2001) and mean or mode, and the error of an imputation."""
import numpy as np
import pandas as pd

from src.data import numeric_attributes

# Memory limit for one block of the distance matrix (number of float64 values).
BLOCK_VALUES = 5_000_000


def impute_mean_mode(df: pd.DataFrame) -> pd.DataFrame:
    """Replace each missing value with the mean (numeric attribute) or the mode (symbolic attribute)."""
    out = df.copy()
    numeric = numeric_attributes(df)
    for column in df.columns.drop("class"):
        value = df[column].mean() if column in numeric else df[column].mode().iloc[0]
        out[column] = out[column].fillna(value)
    return out


def _encode(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return the values as floats (category codes for symbolic attributes, NaN if missing) and a numeric flag."""
    attributes = list(df.columns.drop("class"))
    numeric = set(numeric_attributes(df))
    values = np.empty((len(df), len(attributes)))
    for a, column in enumerate(attributes):
        if column in numeric:
            values[:, a] = df[column].to_numpy(dtype=float)
        else:
            codes = df[column].cat.codes.to_numpy().astype(float)
            codes[codes < 0] = np.nan
            values[:, a] = codes
    is_numeric = np.array([c in numeric for c in attributes])
    return values, is_numeric, attributes


def _gower_distances(values: np.ndarray, is_numeric: np.ndarray, rows: np.ndarray) -> np.ndarray:
    """Gower distance from each record in rows to all records.

    A numeric attribute gives |x - y| / range, a symbolic attribute gives 0 (equal) or 1 (not equal).
    The distance is the mean over the attributes that the two records both have.
    Troyanskaya et al. also use only these attributes. Two records with no common attribute have the distance inf.
    """
    span = np.nanmax(values, axis=0) - np.nanmin(values, axis=0)
    span[~is_numeric | (span == 0)] = 1.0
    total = np.zeros((len(rows), len(values)))
    count = np.zeros((len(rows), len(values)))
    for a in range(values.shape[1]):
        x = values[rows, a][:, None]
        y = values[:, a][None, :]
        d = np.abs(x - y) / span[a] if is_numeric[a] else (x != y).astype(float)
        both = ~np.isnan(x) & ~np.isnan(y)
        total += np.where(both, d, 0.0)
        count += both
    with np.errstate(invalid="ignore", divide="ignore"):
        distance = np.where(count > 0, total / count, np.inf)
    distance[np.arange(len(rows)), rows] = np.inf
    return distance


def impute_knn(df: pd.DataFrame, k: int = 10) -> pd.DataFrame:
    """Replace each missing value with an estimate from the k nearest records that have this value.

    A numeric value is the weighted mean, a symbolic value is the weighted mode of the neighbours.
    The weight of a neighbour is 1 / distance, as in Troyanskaya et al.
    If no record has a finite distance, the function uses the mean or the mode.
    """
    values, is_numeric, attributes = _encode(df)
    missing = np.isnan(values)
    incomplete = np.flatnonzero(missing.any(axis=1))
    filled = values.copy()
    block = max(1, BLOCK_VALUES // len(df))
    for start in range(0, len(incomplete), block):
        rows = incomplete[start:start + block]
        distance = _gower_distances(values, is_numeric, rows)
        for a in range(len(attributes)):
            targets = np.flatnonzero(missing[rows, a])
            if len(targets) == 0:
                continue
            d = np.where(missing[:, a][None, :], np.inf, distance[targets])
            kk = min(k, d.shape[1])
            nearest = np.argpartition(d, kk - 1, axis=1)[:, :kk]
            near_d = np.take_along_axis(d, nearest, axis=1)
            # A distance of 0 must not give an infinite weight.
            weights = np.where(np.isfinite(near_d), 1.0 / (near_d + 1e-6), 0.0)
            near_v = values[nearest, a]
            for t, w, v in zip(rows[targets], weights, near_v):
                if w.sum() == 0:
                    continue
                if is_numeric[a]:
                    filled[t, a] = np.dot(w, v) / w.sum()
                else:
                    filled[t, a] = np.bincount(v.astype(int), weights=w).argmax()
    out = df.copy()
    for a, column in enumerate(attributes):
        if is_numeric[a]:
            out[column] = filled[:, a]
        else:
            codes = np.where(np.isnan(filled[:, a]), -1, filled[:, a]).astype(int)
            out[column] = pd.Categorical.from_codes(codes, dtype=df[column].dtype)
    # Records with no neighbour keep NaN, so the fallback fills them.
    return impute_mean_mode(out)


def imputation_error(true: pd.DataFrame, imputed: pd.DataFrame, removed: np.ndarray) -> dict:
    """Error of an imputation on the removed values (the mask of add_mcar).

    nrmse: the RMS error on the numeric attributes. Each attribute is divided by its standard deviation in the
    true table, so attributes with different scales have the same weight. Troyanskaya et al. divide by the mean
    of one table, but our attributes have different scales.
    error_rate: the fraction of wrong values on the symbolic attributes.
    """
    attributes = list(true.columns.drop("class"))
    numeric = set(numeric_attributes(true))
    squared, wrong, n_numeric, n_symbolic = 0.0, 0, 0, 0
    for a, column in enumerate(attributes):
        mask = removed[:, a]
        if not mask.any():
            continue
        t = true[column].to_numpy()[mask]
        e = imputed[column].to_numpy()[mask]
        if column in numeric:
            std = true[column].std() or 1.0
            squared += np.sum(((e.astype(float) - t.astype(float)) / std) ** 2)
            n_numeric += mask.sum()
        else:
            wrong += np.sum(e != t)
            n_symbolic += mask.sum()
    return {
        "nrmse": float(np.sqrt(squared / n_numeric)) if n_numeric else None,
        "error_rate": float(wrong / n_symbolic) if n_symbolic else None,
    }
