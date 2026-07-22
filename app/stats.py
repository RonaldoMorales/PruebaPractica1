"""
Funciones estadísticas aceleradas con Numba para GameScout.
"""

import numpy as np
from numba import njit


@njit
def category_stats(prices, type_ids):
    """
    Calcula estadísticas por categoría.

    Parameters
    ----------
    prices : np.ndarray
        Precios de los productos.

    type_ids : np.ndarray
        IDs de categoría.

    Returns
    -------
    tuple
        (categories, counts, mins, maxs, means, stds)
    """

    categories = np.unique(type_ids)

    n = len(categories)

    counts = np.zeros(n, dtype=np.int64)
    mins = np.zeros(n, dtype=np.float64)
    maxs = np.zeros(n, dtype=np.float64)
    means = np.zeros(n, dtype=np.float64)
    stds = np.zeros(n, dtype=np.float64)

    for i in range(n):

        category = categories[i]

        total = 0.0
        count = 0

        minimum = 0.0
        maximum = 0.0

        # Primera pasada
        for j in range(len(prices)):

            if type_ids[j] == category:

                price = prices[j]

                if count == 0:
                    minimum = price
                    maximum = price
                else:
                    if price < minimum:
                        minimum = price

                    if price > maximum:
                        maximum = price

                total += price
                count += 1

        mean = total / count

        # Segunda pasada
        variance = 0.0

        for j in range(len(prices)):

            if type_ids[j] == category:

                diff = prices[j] - mean
                variance += diff * diff

        variance /= count

        std = np.sqrt(variance)

        counts[i] = count
        mins[i] = minimum
        maxs[i] = maximum
        means[i] = mean
        stds[i] = std

    return categories, counts, mins, maxs, means, stds


@njit
def price_zscores(prices, type_ids):
    """
    Calcula el z-score por categoría usando Numba.
    """

    zscores = np.zeros(len(prices), dtype=np.float64)

    categories = np.unique(type_ids)

    for i in range(len(categories)):

        category = categories[i]

        total = 0.0
        count = 0

        # Promedio
        for j in range(len(prices)):

            if type_ids[j] == category:

                total += prices[j]
                count += 1

        mean = total / count

        # Desviación estándar
        variance = 0.0

        for j in range(len(prices)):

            if type_ids[j] == category:

                diff = prices[j] - mean
                variance += diff * diff

        variance /= count

        std = np.sqrt(variance)

        # Z-score
        for j in range(len(prices)):

            if type_ids[j] == category:

                if std == 0.0:
                    zscores[j] = 0.0
                else:
                    zscores[j] = (prices[j] - mean) / std

    return zscores


def price_zscores_python(prices, type_ids):
    """
    Misma implementación que price_zscores,
    pero sin Numba para el benchmark.
    """

    zscores = np.zeros(len(prices), dtype=np.float64)

    categories = np.unique(type_ids)

    for category in categories:

        total = 0.0
        count = 0

        for i in range(len(prices)):

            if type_ids[i] == category:

                total += prices[i]
                count += 1

        mean = total / count

        variance = 0.0

        for i in range(len(prices)):

            if type_ids[i] == category:

                diff = prices[i] - mean
                variance += diff * diff

        variance /= count

        std = np.sqrt(variance)

        for i in range(len(prices)):

            if type_ids[i] == category:

                if std == 0.0:
                    zscores[i] = 0.0
                else:
                    zscores[i] = (prices[i] - mean) / std

    return zscores
