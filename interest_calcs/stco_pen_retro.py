# ...

# ...
__all__ = ['PKG_DIR', 'RATES', 'load_rates', 'get_breakdown', 'calc_stco_pen_retro']

# ...
import typing as t

import pandas as pd
import pkg_resources

from .core import fix_round, fp

PKG_DIR = pkg_resources.resource_filename(__name__, ".")

# ...
# ...
def load_rates(src: str = fp("../dat/int_rates.csv")) -> dict:
    """...

    Parameters
    ----------
    src : str, optional
        str

    Returns
    -------
    dict
        dict
    """
    int_rates = pd.read_csv(src)
    int_rates = int_rates[["Year", "Monthly Interest Rate"]].copy()
    int_rates = int_rates.set_index("Year")
    interest_dict = int_rates.to_dict()["Monthly Interest Rate"]
    print(
        f"Loaded rates for {list(interest_dict.keys())[0]} to {list(interest_dict.keys())[-1]}"
    )
    return interest_dict


RATES = load_rates()

# ...
# ...
def get_breakdown(pmt_date: pd.Timestamp, dor: pd.Timestamp) -> dict:
    """Find number of years included in the retro payment and number of months for each year

    Parameters
    ----------
    pmt_date : pd.Timestamp
        pd.Timestamp - can be formatted as str
    dor : pd.Timestamp
        pd.Timestamp - can be formatted as str

    Returns
    -------
    dict
        dict[int, int] - num months per year the retro payment spans
    """
    pmt_date = pd.to_datetime(pmt_date)
    dor = pd.to_datetime(dor)

    breakdown = pd.DataFrame()
    breakdown["range"] = pd.date_range(start=dor, end=pmt_date, freq="MS")
    breakdown = breakdown.iloc[:-1].copy()
    breakdown["year"] = breakdown["range"].dt.year
    breakdown = breakdown.groupby("year", as_index=False).count().copy()
    return breakdown.set_index("year").to_dict()["range"]

# ...
# ...
def _cum_val(dor: pd.Timestamp, pmt_date: pd.Timestamp, pmt_amt: float) -> float:
    """helper

    Parameters
    ----------
    dor : pd.Timestamp
        pd.Timestamp - can be formatted as str
    pmt_date : pd.Timestamp
        pd.Timestamp - can be formatted as str
    pmt_amt : float
        float

    Returns
    -------
    float
        float - total retro + interest
    """
    import numpy_financial as npf

    breakdown = get_breakdown(pmt_date, dor)
    num_years = len(breakdown)
    num_months_retro = sum([breakdown[k] for k in breakdown])

    if num_years == 1:
        return fix_round(
            npf.fv(
                RATES[pd.to_datetime(dor).year],
                num_months_retro,
                pmt_amt,
                0,
                when="begin",
            )
            * -1,
            2,
        )
    max_year = max(breakdown.keys())
    cum_values = []
    for k in breakdown:
        cum_value = 0
        t_year = k
        cum_value += npf.fv(RATES[k], breakdown[k], pmt_amt, 0, when="begin")

        while t_year < max_year:
            cum_value *= (1 + RATES[t_year + 1]) ** (breakdown[t_year + 1])
            t_year += 1
        cum_values.append(cum_value)
    return fix_round(sum(cum_values) * -1, 2)

# ...
# ...
def calc_stco_pen_retro(
    dor: pd.Timestamp,
    pmt_date: pd.Timestamp,
    pmt_amt: t.Union[float, int],
    bridge_end: pd.Timestamp = None,
) -> float:
    """...

    Parameters
    ----------
    dor : pd.Timestamp
        pd.Timestamp - can be formatted as str
    pmt_date : pd.Timestamp
        pd.Timestamp - can be formatted as str
    pmt_amt : t.Union[float, int]
        t.Union[float, int]
    bridge_end : pd.Timestamp, optional
        Only need to include if there's a bridge that ended before `pmt_date`. Can be formatted as string. Should be last day of month - eg. '31-may-2023'

    Returns
    -------
    float
        float
    """
    dor = pd.to_datetime(dor)
    pmt_date = pd.to_datetime(pmt_date)

    if bridge_end:
        bridge_end = pd.to_datetime(bridge_end)

        if bridge_end < pmt_date:
            og_pmt_date = pmt_date
            pmt_date = bridge_end + pd.Timedelta(days=1)  # 1st of next month
            cv = _cum_val(dor, pmt_date, pmt_amt)
            roll_fwd = get_breakdown(og_pmt_date, pmt_date)
            x = 1
            for k in roll_fwd:
                x *= (1 + RATES[k]) ** (roll_fwd[k])
            cv *= x
            return fix_round(cv, 2)

        return _cum_val(dor, pmt_date, pmt_amt)

    return _cum_val(dor, pmt_date, pmt_amt)
