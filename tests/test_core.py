"""Tests of the data, the simulation of missing values, the imputation and the tolerance relation."""
import numpy as np
import pandas as pd
import pytest

from src.data import SPECS, load_dataset, numeric_attributes
from src.impute import imputation_error, impute_knn, impute_mean_mode
from src.missing import add_mcar
from src.rough import (count, cut_points, discretize, encode, generalized_decision, lower_approximation, pack,
                       tolerance_classes, unpack, upper_approximation)

# Records, attributes and numeric attributes from the UCI descriptions.
SHAPES = {"voting": (435, 16, 0), "hepatitis": (155, 19, 6), "mushroom": (8124, 22, 0),
          "car": (1728, 6, 0), "wdbc": (569, 30, 30), "adult": (48842, 14, 6)}


def cars() -> pd.DataFrame:
    """Table 2 of Kryszkiewicz (1998). None is a missing value."""
    return pd.DataFrame({
        "price": ["high", "low", None, "high", None, "low"],
        "mileage": ["high", None, None, None, None, "high"],
        "size": ["full", "full", "compact", "full", "full", "full"],
        "max_speed": ["low", "low", "low", "high", "high", None],
        "class": ["good", "good", "poor", "good", "excellent", "good"],
    }).astype("category")


def direct_sim(codes: np.ndarray) -> np.ndarray:
    """SIM from its definition, with no bit sets."""
    x, y = codes[:, None, :], codes[None, :, :]
    return ((x == y) | (x == -1) | (y == -1)).all(axis=2)


@pytest.mark.parametrize("name", SPECS)
def test_load_dataset(name):
    df = load_dataset(name)
    n, m, numeric = SHAPES[name]
    assert df.shape == (n, m + 1)
    assert df.columns[-1] == "class"
    assert df["class"].notna().all()
    assert len(numeric_attributes(df)) == numeric


def test_add_mcar():
    df = load_dataset("car")
    out, removed = add_mcar(df, 0.3, seed=0)
    assert removed.sum() == round(0.3 * df.shape[0] * (df.shape[1] - 1))
    assert out.drop(columns="class").isna().to_numpy()[removed].all()
    assert out["class"].equals(df["class"])
    assert out.dtypes.equals(df.dtypes)
    assert out.equals(add_mcar(df, 0.3, seed=0)[0])


def test_imputation():
    df = load_dataset("wdbc")
    missing, removed = add_mcar(df, 0.1, seed=0)
    knn = impute_knn(missing, k=10)
    mean = impute_mean_mode(missing)
    assert knn.notna().all().all() and knn.dtypes.equals(df.dtypes)
    assert imputation_error(df, knn, removed)["nrmse"] < imputation_error(df, mean, removed)["nrmse"]


def test_knn_symbolic():
    df = load_dataset("voting")
    missing, removed = add_mcar(df, 0.1, seed=0)
    knn = impute_knn(missing, k=10)
    assert knn.notna().all().all() and knn.dtypes.equals(df.dtypes)
    error = imputation_error(df, knn, removed)["error_rate"]
    assert error < imputation_error(df, impute_mean_mode(missing), removed)["error_rate"]


def test_paper_example():
    codes, decision, names = encode(cars())
    classes = tolerance_classes(codes)
    expected = [{1}, {2, 6}, {3}, {4, 5}, {4, 5, 6}, {2, 5, 6}]
    assert [set(np.flatnonzero(row) + 1) for row in unpack(classes, 6)] == expected
    general = generalized_decision(classes, decision)
    assert [{names[d] for d in np.flatnonzero(row)} for row in general] == [
        {"good"}, {"good"}, {"poor"}, {"good", "excellent"}, {"good", "excellent"}, {"good", "excellent"}]
    good = pack(decision == names.index("good"))
    assert list(np.flatnonzero(lower_approximation(classes, good)) + 1) == [1, 2]
    assert list(np.flatnonzero(upper_approximation(classes, good)) + 1) == [1, 2, 4, 5, 6]


@pytest.mark.parametrize("name,fraction", [("voting", 0.0), ("car", 0.3), ("hepatitis", 0.2), ("wdbc", 0.1)])
def test_tolerance_classes(name, fraction):
    df, _ = add_mcar(load_dataset(name), fraction, seed=1)
    codes, _, _ = encode(discretize(df, cut_points(df, 4)))
    expected = direct_sim(codes)
    classes = tolerance_classes(codes)
    assert (unpack(classes, len(df)) == expected).all()
    assert (count(classes) == expected.sum(axis=1)).all()
    subset = [0, 2]
    assert (unpack(tolerance_classes(codes, subset), len(df)) == direct_sim(codes[:, subset])).all()


def test_discretize():
    df = load_dataset("hepatitis")
    cuts = cut_points(df, 4)
    out = discretize(df, cuts)
    assert not numeric_attributes(out)
    for column in cuts:
        assert out[column].isna().equals(df[column].isna())
        assert out[column].nunique() <= 4
