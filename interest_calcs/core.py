"""..."""

# ...

# %% auto 0
__all__ = ['loadSerializedLog', 'setupLogger', 'fp', 'yaml_helper', 'fix_round']


import json
import math
import os
import pathlib
import typing as t
from typing import Any, Optional, Union

import pandas as pd
import pytest
import yaml
from loguru import logger as lg


def _getDFFromSerializedLog(log_fp: str) -> pd.DataFrame:
    """-> pd.DataFrame

    Parameters
    ----------
    log_fp : str
        str

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
    with open(log_fp, "r") as f:
        contents = f.read().strip()
    t_logs = contents.split("\n")

    t_dicts = []
    for l in t_logs:
        t_dicts.append(json.loads(l))

    t_dfs = []
    for d in t_dicts:
        t_dfs.append(pd.DataFrame().from_dict(d, orient="index").T)

    concat = pd.concat(t_dfs)
    return concat.reset_index(drop=True).copy()


def _cleanLogDF(df: pd.DataFrame) -> pd.DataFrame:
    """-> pd.DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        pd.DataFrame

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
    df["msg"] = df["text"].str.strip()
    df["fx"] = df["record"].apply(lambda x: x.get("function"))
    df["time_repr"] = df["record"].apply(lambda x: x.get("time").get("repr"))
    df["time_unix"] = df["record"].apply(lambda x: str(x.get("time").get("timestamp")))
    df["lvl"] = df["record"].apply(lambda x: x.get("level").get("name"))
    rel_cols = ["lvl", "time_repr", "fx", "msg", "record", "time_unix"]
    return df[rel_cols].copy()  # type: ignore


def loadSerializedLog(
    log_fp: str, incl_full_record: bool = False, incl_unix_ts: bool = False
) -> pd.DataFrame:
    """-> pd.DataFrame

    Parameters
    ----------
    log_fp : str
        str
    incl_full_record : bool, optional
        bool
    incl_unix_ts : bool, optional
        bool

    Returns
    -------
    pd.DataFrame
        pd.DataFrame
    """
    df = _getDFFromSerializedLog(log_fp)
    df = _cleanLogDF(df)

    if not incl_full_record:
        del df["record"]
    if not incl_unix_ts:
        del df["time_unix"]

    return df.copy()


def setupLogger(name: str = "log", serialize: bool = False) -> None:
    """add handler attached to `<name>.log` @ trace level and up

    Parameters
    ----------
    name : str, optional
        str
    serialize : bool, optional
        bool
    """
    if not serialize:
        _handlers: dict = lg._core.handlers  # type: ignore
        if _handlers.get(0):
            pass
        if not _handlers.get(1):
            lg.add(
                f"{name}.log",
                format="{time} | {level} | {function} | {message}",
                level=5,
            )
    else:
        _handlers: dict = lg._core.handlers  # type: ignore
        if _handlers.get(0):
            pass
        if not _handlers.get(1):
            lg.add(
                f"{name}.log",
                format="{message}",
                level=5,
                serialize=True,
            )


setupLogger(name="interest_calcs", serialize=False)
lg.trace("init logging")


def fp(_path: str = "", ambiguous_err: bool = True) -> str:
    """For referencing relative file paths in dev env. Assumes core is always one level down from project root directory.

    Parameters
    ----------
    _path : str, optional
        str - eg. `"../dat/some_file.csv"` == `"<project_root>/dat/some_file.csv>"`
    ambiguous_err : bool, optional
        bool - if True, will raise exception if path is ambiguous when running docs generation vs dev env

    Returns
    -------
    str
        str
    """
    nbs_path = pathlib.Path(globals().get("__file__", "./_")).absolute().parent

    _rfp = _path.replace("\\", "/")
    _same_lvl = _rfp.replace("../", "./", 1)
    if not _rfp.startswith("../"):
        raise Exception("invalid path")

    rfp = pathlib.Path.joinpath(nbs_path, _rfp).resolve()
    same_lvl = pathlib.Path.joinpath(nbs_path, _same_lvl).resolve()

    if ambiguous_err:
        if rfp.exists() and same_lvl.exists():
            raise Exception("Ambiguous path")

    if rfp.exists():
        return str(rfp)
    elif same_lvl.exists():
        return str(same_lvl)
    else:
        raise Exception("invalid path")


def yaml_helper(
    fpath: str = "./config.yaml",
    mode: str = "r",
    data: Optional[dict] = None,
) -> dict:
    """Helper function to read, write, append to files in yaml format. Checks for duplicate keys if reading or appending.

    Parameters
    ----------
    fpath : str, optional
        str
    mode : str, optional
        str - r / a / w
    data : dict, optional
        cannot be None if writing or appending

    Returns
    -------
    dict
        dict - data if reading, {'r': 0} if writing/appending
    """
    mode = mode.lower().strip()
    assert mode in ["r", "a", "w"], "Invalid mode"

    if mode == "r":

        class UniqueKeyLoader(yaml.SafeLoader):
            def construct_mapping(self, node, deep=False) -> dict:
                mapping = []
                for key_node, value_node in node.value:
                    key = self.construct_object(key_node, deep=deep)
                    assert key not in mapping, f"Duplicate key detected: {key}"
                    mapping.append(key)
                return super().construct_mapping(node, deep)

        with open(fpath, "r", encoding="utf-8") as f:
            dat: dict = yaml.load(f.read(), Loader=UniqueKeyLoader)
        return dat

    elif mode == "w":
        assert data is not None, "Data is None"
        with open(fpath, "w", encoding="utf-8") as f:
            f.write((yaml.dump(data, default_flow_style=False, sort_keys=False)))
        return {"r": 0}

    else:
        assert data is not None, "Data is None"
        existing_keys = list(yaml_helper(fpath, mode="r").keys())
        for k in existing_keys:
            assert k not in list(data.keys()), f"Duplicate key detected: {k}"

        with open(fpath, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write((yaml.dump(data, default_flow_style=False, sort_keys=False)))
        return {"r": 0}


def fix_round(num: float | int, position: int = 0) -> float:
    """Python's built-in `round` function can return unexpected results. See `https://docs.python.org/3/library/functions.html#round`. This function returns the same result as the Excel `ROUND` function.

    Parameters
    ----------
    num : float | int
        float | int
    position : int, optional
        int

    Returns
    -------
    float
        float
    """
    if isinstance(num, (float, int)):
        multiplier = 10**position
        num = multiplier * num
        after_decimal = str(float(num)).split(".")[1]
        if after_decimal == "5":
            if num > 0:
                x = math.ceil(num)
            else:
                x = math.floor(num)
            return round(x / multiplier, position)
        return round(num / multiplier, position)
    raise Exception("Invalid input for `num`")
