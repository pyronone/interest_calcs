# interest_calcs


<!-- ... -->

> All interest calc related scripts/functions I’ve used at TH

[Documentation](https://pyronone.github.io/interest_calcs/index.html)

## Installation

    !git clone https://github.com/pyronone/interest_calcs.git
    %cd './interest_calcs'
    !pip install -e ".[dev]"

## Quick Example

``` python
from interest_calcs.srs import calc_pv

pv, work, rf = calc_pv(
    int_rate_input=2.3,
    num_periods=40,
    amt_inputs=[(74.00, "1-may-2020"), (80.58, "1-may-2021")],
)
pv
```

    3028.87

``` python
work.head(15)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|     | compounded_int | amt   | pmt_no | month      | mult      | monthly_rate | pv@1-may-2020 |
|-----|----------------|-------|--------|------------|-----------|--------------|---------------|
| 0   | 1.078745       | 74.00 | 1      | 2020-05-01 | 79.827127 | 0.001897     | 3028.871251   |
| 1   | 1.076703       | 74.00 | 2      | 2020-06-01 | 79.676001 |              |               |
| 2   | 1.074664       | 74.00 | 3      | 2020-07-01 | 79.525162 |              |               |
| 3   | 1.072630       | 74.00 | 4      | 2020-08-01 | 79.374607 |              |               |
| 4   | 1.070599       | 74.00 | 5      | 2020-09-01 | 79.224338 |              |               |
| 5   | 1.068572       | 74.00 | 6      | 2020-10-01 | 79.074354 |              |               |
| 6   | 1.066549       | 74.00 | 7      | 2020-11-01 | 78.924653 |              |               |
| 7   | 1.064530       | 74.00 | 8      | 2020-12-01 | 78.775236 |              |               |
| 8   | 1.062515       | 74.00 | 9      | 2021-01-01 | 78.626102 |              |               |
| 9   | 1.060503       | 74.00 | 10     | 2021-02-01 | 78.477250 |              |               |
| 10  | 1.058496       | 74.00 | 11     | 2021-03-01 | 78.328679 |              |               |
| 11  | 1.056492       | 74.00 | 12     | 2021-04-01 | 78.180390 |              |               |
| 12  | 1.054492       | 80.58 | 13     | 2021-05-01 | 84.970937 |              |               |
| 13  | 1.052495       | 80.58 | 14     | 2021-06-01 | 84.810073 |              |               |
| 14  | 1.050503       | 80.58 | 15     | 2021-07-01 | 84.649514 |              |               |

</div>

``` python
rf.head(10)
```

<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }
&#10;    .dataframe tbody tr th {
        vertical-align: top;
    }
&#10;    .dataframe thead th {
        text-align: right;
    }
</style>

|     | pmt_date   | num_months | amt_100pct | amt_71pct |
|-----|------------|------------|------------|-----------|
| 0   | 2025-02-01 | 57         | 3374.35    | 2395.79   |
| 1   | 2025-03-01 | 58         | 3380.75    | 2400.33   |
| 2   | 2025-04-01 | 59         | 3387.16    | 2404.88   |
| 3   | 2025-05-01 | 60         | 3393.59    | 2409.45   |
| 4   | 2025-06-01 | 61         | 3400.02    | 2414.01   |
| 5   | 2025-07-01 | 62         | 3406.47    | 2418.59   |
| 6   | 2025-08-01 | 63         | 3412.93    | 2423.18   |
| 7   | 2025-09-01 | 64         | 3419.41    | 2427.78   |
| 8   | 2025-10-01 | 65         | 3425.89    | 2432.38   |
| 9   | 2025-11-01 | 66         | 3432.39    | 2437.00   |

</div>

## Changelog

### 1.0.1

- updated minimum Python version to 3.10

### 0.1.1

- removed unused modules
