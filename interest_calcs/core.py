# ...

# ...
__all__ = ['PKG_DIR', 'fp', 'yaml_helper', 'fix_round']

# ...
import os
import typing as t
import pkg_resources
import yaml

PKG_DIR = pkg_resources.resource_filename(__name__, ".")

# ...
# ...
def fp(relative_fp: str, base_dir: str = PKG_DIR) -> str:
    """For referencing relative file paths in package directory.

    Parameters
    ----------
    relative_fp : str
        str - eg. "../dir/file.txt"
    base_dir : str, optional
        str

    Returns
    -------
    str
        str
    """
    docs_mode = not os.path.exists(os.path.join(base_dir, relative_fp))

    if docs_mode:
        relative_fp = relative_fp.replace("..", ".", 1)

    return os.path.join(base_dir, relative_fp)


def yaml_helper(
    fpath: str = "./config.yaml",
    mode: str = "r",
    data: dict = None,
) -> dict:
    """Helper function to read, write, append to files in yaml format. Checks for duplicate keys if reading or appending.

    Parameters
    ----------
    fpath : str, optional
        str
    mode : str, optional
        str - r / a / w
    data : dict, optional
        dict - cannot be None if writing or appending

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
            data = yaml.load(f.read(), Loader=UniqueKeyLoader)
        return data

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

# ...
# ...
def fix_round(num: t.Union[float, int], position: int = 0) -> float:
    """Python's built-in `round` function can return unexpected results. See `https://docs.python.org/3/library/functions.html#round`. This function returns the same result as the Excel `ROUND` function..

    Parameters
    ----------
    num : ty.Union[float, int]
        float or int
    position : int, optional
        int

    Returns
    -------
    float
        float
    """
    import math

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
