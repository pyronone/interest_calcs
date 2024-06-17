# ...

# ...
__all__ = ['PKG_DIR', 'calc_pv']

# ...
import pandas as pd
import pkg_resources

from .core import fix_round

PKG_DIR = pkg_resources.resource_filename(__name__, ".")

# ...
# ...
def _get_dt_suffix() -> str:
    from datetime import datetime

    now = datetime.now()
    return now.strftime("_%Y%m%d_%H%M")

# ...
# ...
def _get_monthly_compounded_rate(annual_rate: float) -> float:
    """...

    Parameters
    ----------
    annual_rate : float
        float - eg. 4.1, 2.3, etc

    Returns
    -------
    float
        float
    """
    return (((100 + annual_rate) / 100) ** (1 / 12)) - 1

# ...
# ...
def _create_df(
    compounded_ints: list,
    monthly_pmt: float,
    first_pmt_date: str,
    amt_inputs: list[tuple],
    interest_rate: float,
    num_periods: int,
) -> pd.DataFrame:
    df = pd.DataFrame()
    df["compounded_int"] = compounded_ints[::-1]
    df["amt"] = [monthly_pmt] * len(df)
    df["pmt_no"] = list(range(1, len(compounded_ints) + 1))
    df["month"] = pd.date_range(
        start=first_pmt_date, periods=len(compounded_ints), freq="MS"
    )

    # add new amounts
    if amt_inputs is None:
        amt_inputs = []
    else:
        for i in amt_inputs:
            new_amt = i[0]
            eff_date = pd.to_datetime(i[1])

            mask = df["month"] >= eff_date
            df.loc[mask, "amt"] = new_amt

    # multiply and find PV based on FV
    df["mult"] = df["compounded_int"] * df["amt"]
    pv = df.mult.sum() / ((1 + interest_rate) ** num_periods)
    df["monthly_rate"] = [interest_rate] + ([""] * (len(df) - 1))
    df[f"pv@{first_pmt_date}"] = [pv] + ([""] * (len(df) - 1))

    return df


def _export_df(df: pd.DataFrame) -> None:
    suffix = _get_dt_suffix()
    df.to_excel(f"work{suffix}.xlsx", index=False)

# ...
# ...
def calc_pv(
    monthly_pmt: float,
    int_rate_input: float,
    num_periods: int,
    first_pmt_date: str,
    amt_inputs: list[tuple] = None,
    _export: bool = True,
) -> tuple:
    """Assumes constant interest rate

    Parameters
    ----------
    monthly_pmt : float
        float
    int_rate_input : float
        pct - eg. 4.1, 2.3, etc.
    num_periods : int
        int
    first_pmt_date : str
        str representation of date - eg. '1-may-2020'
    amt_inputs : list[tuple], optional
        list[tuple] - where each tuple has 2 elements: new amount and effective date. if the amounts are constant, use None
    _export : bool, optional
        if True, exports excel file showing work

    Returns
    -------
    tuple
        (pv amount, df showing work)
    """
    interest_rate = _get_monthly_compounded_rate(int_rate_input)
    compounded_ints = []
    for i in range(1, num_periods + 1):
        compounded_int = (1 + interest_rate) ** i
        compounded_ints.append(compounded_int)
    df = _create_df(
        compounded_ints,
        monthly_pmt,
        first_pmt_date,
        amt_inputs,
        interest_rate,
        num_periods,
    )
    if _export:
        _export_df(df)
    return fix_round(df.iloc[0, -1], 2), df
