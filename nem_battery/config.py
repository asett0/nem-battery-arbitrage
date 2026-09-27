from pathlib import Path

from nem_battery.types import Battery, RollingWindow

INTERVAL_MINS = 5
INTERVAL_HOURS = INTERVAL_MINS / 60
INTERVALS_PER_DAY = 24 * 60 // INTERVAL_MINS
HOURS_PER_YEAR = 24 * 365.25

REGION = "SA1"
MONTH = "202608"

RAW_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/outputs")

# The battery starts the period at this state of charge and
# must end at the same level so that revenue is pure arbitrage
INITIAL_SOC_FRACTION = 0.5
ENERGY_MWH = 200.0
BATTERY = Battery(power_mw=100.0, energy_mwh=ENERGY_MWH, soc_mwh=INITIAL_SOC_FRACTION * ENERGY_MWH)

# Generate a plan every 30 minutes over a 24 hour window.
ROLLING = RollingWindow(commit_intervals=6, lookahead_intervals=INTERVALS_PER_DAY)
