from dataclasses import asdict

import pandas as pd

from nem_battery.config import HOURS_PER_YEAR, INTERVAL_HOURS, INTERVALS_PER_DAY
from nem_battery.types import Battery, Dispatch, Revenue


def mode_frame(scored: pd.DataFrame, mode: str, dispatch: Dispatch) -> pd.DataFrame:
    prices = scored["rrp"].to_numpy()
    return pd.DataFrame(
        {
            "settlement_time": scored["settlement_time"].to_numpy(),
            "mode": mode,
            "rrp": prices,
            "charge_mw": dispatch.charge_mw,
            "discharge_mw": dispatch.discharge_mw,
            "soc_mwh": dispatch.soc_mwh,
            "revenue_aud": (dispatch.discharge_mw - dispatch.charge_mw) * prices * INTERVAL_HOURS,
        }
    )


def schedule(data: pd.DataFrame, hindsight: Dispatch, rolling: Dispatch) -> pd.DataFrame:
    """Long-form schedule, one row per interval per mode, scored against actual prices.
    The first day of `data` is forecast history only for naive forecasts
    so both modes exclude the first day.
    """
    scored = data.iloc[INTERVALS_PER_DAY:].reset_index(drop=True)
    return pd.concat(
        [mode_frame(scored, "hindsight", hindsight), mode_frame(scored, "rolling", rolling)],
        ignore_index=True,
    )


def revenue(dispatch_schedule: pd.DataFrame, battery: Battery) -> Revenue:
    hours = len(dispatch_schedule) * INTERVAL_HOURS
    total = float(dispatch_schedule["revenue_aud"].sum())
    return Revenue(
        total_aud=round(total, 2),
        per_mw_year_aud=round(total / battery.power_mw * HOURS_PER_YEAR / hours, 2),
    )


def summary(dispatch_schedule: pd.DataFrame, battery: Battery) -> dict:
    by_mode = dispatch_schedule.groupby("mode")
    hindsight = revenue(by_mode.get_group("hindsight"), battery)
    rolling = revenue(by_mode.get_group("rolling"), battery)
    return {
        "hindsight": asdict(hindsight),
        "rolling": asdict(rolling),
        "rolling_to_hindsight_ratio": round(rolling.total_aud / hindsight.total_aud, 4),
    }
