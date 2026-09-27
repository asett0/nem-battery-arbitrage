import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

from nem_battery.config import INTERVAL_MINS

matplotlib.use("Agg")
plt.style.use("seaborn-v0_8-whitegrid")


def interval_day(settlement_time: pd.Series) -> pd.Series:
    """Calendar day an interval belongs to. AEMO timestamps mark the END of each interval."""
    return (settlement_time - pd.Timedelta(minutes=INTERVAL_MINS)).dt.floor("D")


def daily_revenue(dispatch_schedule: pd.DataFrame) -> pd.DataFrame:
    """Revenue per calendar day, one column per mode."""
    day = interval_day(dispatch_schedule["settlement_time"])
    return dispatch_schedule.groupby([day, "mode"])["revenue_aud"].sum().unstack("mode")


def plot_daily_revenue(dispatch_schedule: pd.DataFrame) -> Figure:
    """Grouped bars of daily revenue."""
    daily = daily_revenue(dispatch_schedule)
    fig, axis = plt.subplots(figsize=(12, 4.5), constrained_layout=True)
    positions = range(len(daily))
    width = 0.4
    for offset, mode in zip((-width / 2, width / 2), daily.columns, strict=True):
        axis.bar([p + offset for p in positions], daily[mode] / 1000, width=width, label=mode)
    axis.set_xticks(list(positions)[::7], [d.strftime("%d %b") for d in daily.index[::7]])
    axis.set_ylabel("Daily Revenue (A$k)")
    axis.set_title("Daily Arbitrage Revenue", loc="left")
    axis.legend(loc="upper left")
    return fig
