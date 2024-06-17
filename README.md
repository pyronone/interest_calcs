# interest_calcs




> Just bundling up all interest calc related scripts/functions I’ve used
> at TH

[Documentation](https://pyronone.github.io/interest_calcs/index.html)

## Installation

    !git clone https://github.com/pyronone/interest_calcs.git
    %cd './interest_calcs'
    !pip install -e ".[dev]"

## Quick Example

<details open class="code-fold">
<summary>Code</summary>

``` python
# * DOC
from interest_calcs import srs_pv as spv

pv, _ = spv.calc_pv(
    monthly_pmt=74,
    int_rate_input=2.3,
    num_periods=40,
    first_pmt_date="1-may-2020",
    amt_inputs=[(80.58, "1-may-2021")],  # amts change
    _export=False,
)
pv
```

</details>

    3028.87
