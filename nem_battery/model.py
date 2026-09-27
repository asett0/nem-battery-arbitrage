import numpy as np
import pulp

from nem_battery.config import INTERVAL_HOURS
from nem_battery.types import Battery, Dispatch, Prices

SOLVER = pulp.PULP_CBC_CMD(msg=False)


def solve(battery: Battery, prices: Prices, final_soc_mwh: float | None) -> Dispatch:
    """Dispatch from the battery's current state over `prices`, ending at `final_soc_mwh` if set."""
    steps = range(len(prices))
    charge = [pulp.LpVariable(f"c_{t}", lowBound=0, upBound=battery.power_mw) for t in steps]
    discharge = [pulp.LpVariable(f"d_{t}", lowBound=0, upBound=battery.power_mw) for t in steps]
    soc = [pulp.LpVariable(f"s_{t}", lowBound=0, upBound=battery.energy_mwh) for t in steps]
    charging = [pulp.LpVariable(f"b_{t}", cat=pulp.LpBinary) for t in steps]

    problem = pulp.LpProblem("battery_dispatch", pulp.LpMaximize)
    problem += pulp.lpSum(
        (discharge[t] - charge[t]) * float(prices[t]) * INTERVAL_HOURS for t in steps
    )
    for t in steps:
        previous = battery.soc_mwh if t == 0 else soc[t - 1]
        problem += soc[t] == previous + (charge[t] - discharge[t]) * INTERVAL_HOURS
        problem += charge[t] <= battery.power_mw * charging[t]
        problem += discharge[t] <= battery.power_mw * (1 - charging[t])
    if final_soc_mwh is not None:
        problem += soc[-1] == final_soc_mwh

    problem.solve(SOLVER)
    assert pulp.LpStatus[problem.status] == "Optimal"
    return Dispatch(
        charge_mw=np.array([v.value() for v in charge]),
        discharge_mw=np.array([v.value() for v in discharge]),
        soc_mwh=np.array([v.value() for v in soc]),
    )
