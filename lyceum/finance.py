"""Pure financial math — the functional core for the money tools.

These functions contain NO Tkinter, no database, no I/O — only arithmetic on
plain values. They were extracted verbatim from the BookReader GUI class (the
first step of dismantling that God Object, per the audit's Q3) so the math is
unit-testable in isolation and reusable. The GUI methods now delegate here.
"""
from __future__ import annotations


def run_rate_months(cash, monthly):
    """Months of survival if income stopped today. None if no expenses set."""
    if monthly is None or monthly <= 0:
        return None
    return float(cash) / float(monthly)


def time_cost_hours(price, wage, tax_pct):
    """Hours of work a purchase costs. None if no usable (net) wage."""
    net = float(wage) * (1 - (float(tax_pct or 0) / 100.0))
    if net <= 0:
        return None
    return float(price) / net


def wedge_split(old_wage, new_wage, hours_per_week, pct):
    """Split a raise: half (pct) to savings, half to lifestyle. Returns the
    per-hour increase and the savings/lifestyle amounts per month & year."""
    inc = max(0.0, float(new_wage) - float(old_wage))      # $/hr
    annual = inc * float(hours_per_week) * 52.0
    monthly = annual / 12.0
    f = float(pct) / 100.0
    return {"inc_hr": inc,
            "save_monthly": monthly * f, "save_annual": annual * f,
            "life_monthly": monthly * (1 - f), "life_annual": annual * (1 - f)}


def compound_series(weekly, rate_pct, years, start=0.0):
    """Year-by-year balance of weekly savings compounding at rate_pct.
    Returns a list of length years+1 (balance at the end of each year)."""
    r = float(rate_pct) / 100.0
    annual = float(weekly) * 52.0
    bal = float(start)
    out = [bal]
    for _ in range(max(0, int(years))):
        bal = bal * (1 + r) + annual
        out.append(bal)
    return out


def expected_net_worth(age, income):
    """The Millionaire Next Door formula: age * income / 10."""
    return float(age) * float(income) / 10.0


def fee_future_value(start, monthly, years, gross_pct, fee_pct):
    """Monthly-compounded future value with the fee dragging the return.
    net annual return = gross - fee."""
    net = (float(gross_pct) - float(fee_pct)) / 100.0
    r = net / 12.0
    months = max(0, int(round(float(years) * 12)))
    bal = float(start)
    m = float(monthly)
    for _ in range(months):
        bal = bal * (1 + r) + m
    return bal


def critical_mass(income, wd_rate):
    """Nest egg whose safe withdrawals replace your income. income / rate."""
    if wd_rate <= 0:
        return None
    return float(income) / (float(wd_rate) / 100.0)


def years_until_depleted(nest, annual_withdrawal, return_pct, cap=70):
    """Years a nest egg lasts under annual withdrawals + growth. None = it
    sustains itself indefinitely (growth covers the withdrawals)."""
    if annual_withdrawal <= 0:
        return None
    r = float(return_pct) / 100.0
    bal = float(nest)
    for yr in range(1, cap + 1):
        bal = bal * (1 + r) - annual_withdrawal
        if bal <= 0:
            return yr
    return None
