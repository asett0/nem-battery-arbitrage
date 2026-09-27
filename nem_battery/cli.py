import json
import logging
from pathlib import Path

import pandas as pd
from matplotlib.figure import Figure

from nem_battery.config import BATTERY, MONTH, OUTPUT_DIR, RAW_DIR, REGION, ROLLING
from nem_battery.data import load_prices
from nem_battery.dispatch import hindsight, rolling_window
from nem_battery.metrics import (
    schedule,
    summary,
)
from nem_battery.plots import plot_daily_revenue

log = logging.getLogger(__name__)


def run() -> None:
    data = load_prices(RAW_DIR, MONTH, REGION)
    prices = data["rrp"].to_numpy()
    log.info("%d intervals loaded", len(prices))

    log.info("solving perfect hindsight")
    hind = hindsight(BATTERY, prices)
    log.info("solving rolling window")
    roll = rolling_window(BATTERY, prices, ROLLING)

    dispatch_schedule = schedule(data, hind, roll)
    results = summary(dispatch_schedule, BATTERY)
    figure = plot_daily_revenue(dispatch_schedule)
    write_results(OUTPUT_DIR, dispatch_schedule, results, figure)
    print(json.dumps(results, indent=2))


def write_results(
    output_dir: Path, dispatch_schedule: pd.DataFrame, results: dict, figure: Figure
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "summary.json").write_text(json.dumps(results, indent=2))
    dispatch_schedule.to_csv(output_dir / "dispatch_schedule.csv", index=False)
    figure.savefig(output_dir / "daily_revenue.png", dpi=150)
    log.info("wrote results to %s", output_dir)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    run()


if __name__ == "__main__":
    main()
