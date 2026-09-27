import logging
from dataclasses import replace

import numpy as np

from nem_battery.config import INTERVALS_PER_DAY
from nem_battery.model import solve
from nem_battery.types import Battery, Dispatch, Prices, RollingWindow

log = logging.getLogger(__name__)


def naive_forecast(prices: Prices, start: int, length: int) -> Prices:
    """Yesterday's prices for the same intervals."""
    return prices[start - INTERVALS_PER_DAY : start - INTERVALS_PER_DAY + length]


def hindsight(battery: Battery, prices: Prices) -> Dispatch:
    """Solve the whole period at once with actual prices.

    The first day of `prices` is skipped so the result covers the same period as the
    rolling window, which needs that day as forecast history.
    """
    return solve(battery, prices[INTERVALS_PER_DAY:], battery.soc_mwh)


def rolling_window(battery: Battery, prices: Prices, window: RollingWindow) -> Dispatch:
    """Re-solve a lookahead window every `commit_intervals`,
    keeping only the first `commit_intervals` decisions.

    `prices` must include one extra day at the front, used only as forecast history.
    The returned dispatch covers prices[INTERVALS_PER_DAY:].
    """
    total = len(prices)
    pieces: list[Dispatch] = []
    state = battery
    # Start from the second day so that naive forecast is available
    for start in range(INTERVALS_PER_DAY, total, window.commit_intervals):
        end = min(start + window.lookahead_intervals, total)
        final_soc_mwh = battery.soc_mwh if end == total else None
        forecast = naive_forecast(prices, start, end - start)
        # Solve optimisation for window
        dispatch = solve(state, forecast, final_soc_mwh)
        # Keep only first `commit_intervals`
        step = Dispatch(
            dispatch.charge_mw[: window.commit_intervals],
            dispatch.discharge_mw[: window.commit_intervals],
            dispatch.soc_mwh[: window.commit_intervals],
        )
        state = replace(state, soc_mwh=float(step.soc_mwh[-1]))
        pieces.append(step)
        if start % (INTERVALS_PER_DAY * 10) == 0:
            log.info(
                "rolling window: day %d of %d",
                start // INTERVALS_PER_DAY,
                total // INTERVALS_PER_DAY,
            )
    return Dispatch(
        charge_mw=np.concatenate([p.charge_mw for p in pieces]),
        discharge_mw=np.concatenate([p.discharge_mw for p in pieces]),
        soc_mwh=np.concatenate([p.soc_mwh for p in pieces]),
    )
