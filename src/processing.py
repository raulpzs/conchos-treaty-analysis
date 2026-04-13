"""
processing.py
Reusable functions for the Rio Conchos water crisis analysis.
Author: Raul Alejandro Pérez Saucedo
"""

import pandas as pd
import numpy as np

# ── Constants ──────────────────────────────────────────────────────────
MM3_TO_AF = 810.71          # million cubic meters to acre-feet
ANNUAL_TREATY_TARGET = 350_000    # acre-feet per year
CYCLE_TREATY_TARGET = 1_750_000   # acre-feet per 5-year cycle
MONTHS = ['jan','feb','mar','apr','may','jun',
          'jul','aug','sep','oct','nov','dec']


def load_flow_csv(path: str, label: str, encoding: str = 'latin-1') -> pd.DataFrame:
    """
    Load a HydroShare monthly flow CSV (naturalized or regulated).
    Skips 6 metadata rows, converts MM3 to acre-feet, 
    returns wide-format dataframe with year and month columns.
    
    Parameters
    ----------
    path    : path to CSV file
    label   : short name appended to month columns (e.g. 'ojinaga_nat')
    encoding: file encoding, usually 'latin-1' or 'utf-8-sig'
    
    Returns
    -------
    DataFrame with columns: year, jan_{label} ... dec_{label}
    """
    df = pd.read_csv(path, skiprows=6, header=0, encoding=encoding)
    
    # Normalize column count — some files have trailing column
    if len(df.columns) == 14:
        df.columns = ['year'] + MONTHS + ['extra']
        df = df.drop(columns=['extra'])
    else:
        df.columns = ['year'] + MONTHS

    # Clean year column
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df = df.dropna(subset=['year'])
    df['year'] = df['year'].astype(int)

    # Convert MM3 → acre-feet
    for m in MONTHS:
        df[m] = pd.to_numeric(df[m], errors='coerce') * MM3_TO_AF

    # Rename month columns with label
    df = df.rename(columns={m: f'{m}_{label}' for m in MONTHS})

    return df


def water_year_total(df: pd.DataFrame, label: str) -> pd.DataFrame:
    """
    Aggregate monthly flow to water-year totals.
    Water year runs October 1 – September 30, 
    matching the treaty cycle start date (October 25).
    
    Water year N = Oct(N-1) + Nov(N-1) + Dec(N-1) + Jan(N)...Sep(N)

    Parameters
    ----------
    df    : wide-format monthly dataframe from load_flow_csv
    label : label used in column names

    Returns
    -------
    DataFrame with columns: water_year, flow_{label}
    """
    rows = []
    for wy in sorted(df['year'].unique()):
        prev = df[df['year'] == wy - 1]
        curr = df[df['year'] == wy]
        if prev.empty or curr.empty:
            continue

        oct_dec = prev[[f'oct_{label}',
                         f'nov_{label}',
                         f'dec_{label}']].sum(axis=1).values[0]

        jan_sep = curr[[f'{m}_{label}' for m in
                        ['jan','feb','mar','apr','may',
                         'jun','jul','aug','sep']]].sum(axis=1).values[0]

        rows.append({
            'water_year': wy,
            f'flow_{label}': oct_dec + jan_sep
        })

    return pd.DataFrame(rows)


def compute_capture(df: pd.DataFrame,
                    nat_col: str,
                    reg_col: str,
                    label: str = '') -> pd.DataFrame:
    """
    Compute capture share: (natural - regulated) / natural * 100.
    Negative values (data artifact in early period) are preserved
    but should be clipped to 0 for visualization.

    Parameters
    ----------
    df      : dataframe with natural and regulated annual flow columns
    nat_col : column name for naturalized flow
    reg_col : column name for regulated flow
    label   : optional suffix for output column names

    Returns
    -------
    df with added columns: capture_af_{label}, capture_pct_{label}
    """
    suffix = f'_{label}' if label else ''
    df[f'capture_af{suffix}'] = df[nat_col] - df[reg_col]
    df[f'capture_pct{suffix}'] = (
        df[f'capture_af{suffix}'] / df[nat_col] * 100
    ).round(2)
    return df


def assign_water_year(date_series: pd.Series) -> pd.Series:
    """
    Assign water year to a datetime series.
    Oct-Dec -> following calendar year
    Jan-Sep -> same calendar year
    """
    return date_series.apply(
        lambda d: d.year if d.month >= 10 else d.year - 1
    )


def decade_summary(df: pd.DataFrame,
                   nat_col: str,
                   reg_col: str,
                   cap_col: str) -> pd.DataFrame:
    """
    Summarize flow and capture statistics by decade.
    
    Returns
    -------
    DataFrame indexed by decade string (e.g. '1950s')
    """
    df = df.copy()
    df['decade'] = (df['water_year'] // 10 * 10).astype(str) + 's'

    return df.groupby('decade').agg(
        nat_flow_mean=(nat_col, 'mean'),
        reg_flow_mean=(reg_col, 'mean'),
        capture_pct_mean=(cap_col, 'mean'),
        years_below_target=(reg_col,
                            lambda x: (x < ANNUAL_TREATY_TARGET).sum()),
        n_years=(reg_col, 'count')
    ).round(1)


def treaty_cycle_stats(df: pd.DataFrame, reg_col: str) -> pd.DataFrame:
    """
    Compute 5-year rolling cycle totals and compare to treaty obligation.
    Useful for comparing modeled flows to IBWC official delivery records.
    """
    df = df.sort_values('water_year').copy()
    df['cycle_5yr_total'] = (
        df[reg_col].rolling(5).sum()
    )
    df['cycle_deficit'] = (
        CYCLE_TREATY_TARGET - df['cycle_5yr_total']
    ).clip(lower=0)
    df['cycle_delivery_pct'] = (
        df['cycle_5yr_total'] / CYCLE_TREATY_TARGET * 100
    ).round(1)
    return df
