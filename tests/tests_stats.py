import numpy as np

from app.stats import (
    category_stats,
    price_zscores,
)


def test_category_stats():

    prices = np.array(
        [10.0, 20.0, 30.0, 40.0],
        dtype=np.float64,
    )

    types = np.array(
        [1, 1, 2, 2],
        dtype=np.int64,
    )

    categories, counts, mins, maxs, means, stds = category_stats(
        prices,
        types,
    )

    assert np.array_equal(categories, np.array([1, 2]))
    assert np.array_equal(counts, np.array([2, 2]))
    assert np.allclose(mins, np.array([10.0, 30.0]))
    assert np.allclose(maxs, np.array([20.0, 40.0]))
    assert np.allclose(means, np.array([15.0, 35.0]))


def test_price_zscores():

    prices = np.array(
        [10.0, 20.0, 30.0, 40.0],
        dtype=np.float64,
    )

    types = np.array(
        [1, 1, 2, 2],
        dtype=np.int64,
    )

    z = price_zscores(
        prices,
        types,
    )

    esperado = np.array(
        [-1.0, 1.0, -1.0, 1.0]
    )

    assert np.allclose(
        z,
        esperado,
    )
