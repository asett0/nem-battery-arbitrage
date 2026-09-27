from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Prices = NDArray[np.float64]


@dataclass(frozen=True)
class Battery:
    power_mw: float
    energy_mwh: float
    soc_mwh: float


@dataclass(frozen=True)
class RollingWindow:
    commit_intervals: int
    lookahead_intervals: int


@dataclass(frozen=True)
class Dispatch:
    charge_mw: NDArray[np.float64]
    discharge_mw: NDArray[np.float64]
    soc_mwh: NDArray[np.float64]


@dataclass(frozen=True)
class Revenue:
    total_aud: float
    per_mw_year_aud: float
