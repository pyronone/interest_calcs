# ...

# %% auto 0
__all__ = ['calc_pv', 'pv_calc']


from datetime import datetime

import pandas as pd

from .core import fix_round


def _get_dt_suffix() -> str:
    """...

    Returns
    -------
    str
        str
    """
    now = datetime.now()
    return now.strftime("_%Y%m%d_%H%M%S%f")


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


def _create_df(
    compounded_ints: list,
    monthly_pmt: float,
    first_pmt_date: str,
    amt_inputs: list[tuple],
    interest_rate: float,
    num_periods: int,
) -> pd.DataFrame:
    """...

    Parameters
    ----------
    compounded_ints : list
        list
    monthly_pmt : float
        float
    first_pmt_date : str
        str
    amt_inputs : list[tuple]
        list[tuple]
    interest_rate : float
        float
    num_periods : int
        int

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
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
    """export df showing work

    Parameters
    ----------
    df : pd.DataFrame
        pd.DataFrame
    """
    suffix = _get_dt_suffix()
    df.to_excel(f"work{suffix}.xlsx", index=False)


def _num_months(first_pmt: pd.Timestamp, pmt_date: pd.Timestamp) -> int:
    """does not include `pmt_date`

    Parameters
    ----------
    first_pmt : pd.Timestamp
        pd.Timestamp - 1st of month
    pmt_date : pd.Timestamp
        pd.Timestamp - 1st of month

    Returns
    -------
    int
        int
    """
    first_pmt = pd.to_datetime(first_pmt)
    pmt_date = pd.to_datetime(pmt_date)
    date_list = pd.date_range(start=first_pmt, end=pmt_date, freq="MS").tolist()
    df = pd.DataFrame()
    df["months"] = date_list
    return len(df[:-1])


def _firstDayCurrMonth() -> pd.Timestamp:
    """...

    Returns
    -------
    pd.Timestamp
        pd.Timestamp
    """
    current_date = pd.Timestamp.now()
    return pd.Timestamp(current_date.year, current_date.month, 1)


def _roll_fwd_amts(df: pd.DataFrame) -> pd.DataFrame:
    """...

    Parameters
    ----------
    df : pd.DataFrame
        pd.DataFrame

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
    first_pmt_date = df["month"].tolist()[0]

    start_date = _firstDayCurrMonth()

    months = [start_date + pd.DateOffset(months=i) for i in range(60)]
    month_starts = [m.to_period("M").start_time for m in months]

    t_df = pd.DataFrame()
    t_df["pmt_date"] = month_starts
    t_df["num_months"] = t_df["pmt_date"].apply(
        lambda x: (_num_months(first_pmt_date, x))
    )

    pv = fix_round(df.iloc[0, -1], 2)
    interest_rate = df["monthly_rate"].tolist()[0]

    def _get_roll_fwd_amt(tr: pd.Series, pv: float, interest_rate: float) -> float:
        x = pv * ((1 + (interest_rate)) ** tr["num_months"])
        return fix_round(x, 2)

    t_df["amt_100pct"] = t_df.apply(
        lambda x: _get_roll_fwd_amt(x, pv, interest_rate), axis=1
    )

    t_df["amt_71pct"] = t_df["amt_100pct"].apply(lambda x: fix_round(x * 0.71, 2))

    return t_df.copy()


def calc_pv(
    monthly_pmt: float,
    int_rate_input: float,
    num_periods: int,
    first_pmt_date: str,
    amt_inputs: list[tuple] = None,
    _export: bool = True,
    _export_rf: bool = True,
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
    _export_rf : bool, optional
        if True, exports excel file with roll_fwd amts

    Returns
    -------
    tuple
        (pv amount, df showing work, rf df)
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

    if _export_rf:
        _export_df(_roll_fwd_amts(df))

    return fix_round(df.iloc[0, -1], 2), df, _roll_fwd_amts(df)


def _sortInputTuples(amt_inputs: list[tuple]) -> list[tuple]:
    """...

    Parameters
    ----------
    amt_inputs : list[tuple]
        list[tuple]

    Returns
    -------
    list[tuple]
        list[tuple]
    """
    sorted_tups = [list(x) for x in amt_inputs]
    for t_list in sorted_tups:
        t_list[0] = float(t_list[0])
        t_list.append(pd.to_datetime(t_list[1]))
    sorted_tups.sort(key=lambda x: x[2])
    return [tuple(x[:2]) for x in sorted_tups]



def pv_calc(int_rate_input: float, num_periods: int, amt_inputs: list[tuple]) -> tuple:
    """Wrapper around `calc_pv` to simplify inputs. Always exports dfs showing work and roll fwd amts.

    Parameters
    ----------
    int_rate_input : float
        pct - eg. 4.1, 2.3, etc.
    num_periods : int
        int
    amt_inputs : list[tuple]
        list[tuple] - where each tuple has 2 elements: amount and effective date.

    Returns
    -------
    tuple
        (pv amount, df showing work, rf df)
    """
    t_list = _sortInputTuples(amt_inputs)
    earliest_amts = t_list[0]
    monthly_pmt = earliest_amts[0]
    first_pmt_date = earliest_amts[1]

    if len(t_list) == 1:
        amt_inputs = None
    else:
        amt_inputs = t_list[1:]

    pv, work_df, rf_df = calc_pv(
        monthly_pmt, int_rate_input, num_periods, first_pmt_date, amt_inputs, True, True
    )
    return (pv, work_df, rf_df)
