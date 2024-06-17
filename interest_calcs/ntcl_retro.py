# ...

# ...
__all__ = ['PKG_DIR', 'RATES', 'CANSIM_B14045', 'calc_retro']

# ...
import pandas as pd
import pkg_resources

from .core import fix_round

PKG_DIR = pkg_resources.resource_filename(__name__, ".")

# needs updating
RATES = CANSIM_B14045 = {
    2023: 2.55,
    2022: 2.55,
    2021: 0.75,
    2020: 0.98,
    2019: 1.4500000000000002,
    2018: 1.1900000000000002,
    2017: 1.008333333333333,
    2016: 1.1666666666666665,
    2015: 1.2525,
    2014: 1.4500000000000004,
    2013: 1.4500000000000004,
    2012: 1.5833333333333335,
    2011: 1.710833333333333,
    2010: 1.8383333333333334,
    2009: 1.7583333333333329,
}

# ...
# ...
def _get_dt_suffix() -> str:
    from datetime import datetime

    now = datetime.now()
    return now.strftime("_%Y%m%d_%H%M")


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


def _export_df(df: pd.DataFrame) -> None:
    suffix = _get_dt_suffix()
    df.to_excel(f"work{suffix}.xlsx", index=False)


def _product(t_list: list) -> float:
    from functools import reduce

    x = reduce(lambda x, y: x * y, t_list)
    return x

# ...
# ...
def calc_retro(
    dor: pd.Timestamp,
    pmt_date: pd.Timestamp,
    monthly_pmt: float,
    rates: dict = None,
    amt_inputs: list[tuple] = None,
    _export: bool = True,
) -> pd.DataFrame:
    """...

    Parameters
    ----------
    dor : pd.Timestamp
        can be formatted as str
    pmt_date : pd.Timestamp
        can be formatted as str
    monthly_pmt : float
        for 1st month(s), if amounts change
    rates : dict, optional
        CANSIM B14045
    amt_inputs : list[tuple], optional
        list[tuple] - where each tuple has 2 elements: new amount and effective date. if the amounts are constant, use None
    _export : bool, optional
        if True, exports excel file showing work

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
    if rates is None:
        rates = RATES
        print("No rates provided, using default (may be outdated).")

    dor = pd.to_datetime(dor)
    pmt_date = pd.to_datetime(pmt_date)

    df = pd.DataFrame()
    df["month"] = list(pd.date_range(start=dor, end=pmt_date, freq="MS"))[:-1]
    df["monthly_amt"] = monthly_pmt
    df["monthly_rate"] = df["month"].apply(
        lambda x: _get_monthly_compounded_rate(rates[x.year]) + 1
    )

    accumulated = []
    for i in range(len(df)):
        t_list = df["monthly_rate"].tolist()[i : len(df)]
        accumulated.append(_product(t_list))

    df["accum_rate"] = accumulated

    # add new amounts
    if amt_inputs is None:
        amt_inputs = []
    else:
        for i in amt_inputs:
            new_amt = i[0]
            eff_date = pd.to_datetime(i[1])

            mask = df["month"] >= eff_date
            df.loc[mask, "monthly_amt"] = new_amt

    df["monthly_pen_w_int"] = df.monthly_amt * df.accum_rate

    if _export:
        _export_df(df)

    return df
