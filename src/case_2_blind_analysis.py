"""
Case 2: Inter-Event Interval Analysis - Blind Study (Approach Two)
Loads timestamp data, calculates inter-event intervals, and tests for
temporal clustering using chi-square uniformity (log-binned), KS test
against exponential distribution, and coefficient of variation analysis.
Outputs results to output/case_2_results_blind.json.
"""

import json
import os
import numpy as np
import pandas as pd
from scipy import stats

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'timestamp_vals.csv')
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_2_results_blind.json')

N_BINS = 16


def load_and_preprocess(path=DATA_PATH):
    """Load timestamp data, sort chronologically, calculate inter-event intervals in days."""
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Calculate inter-event intervals
    deltas = df['timestamp'].diff().dropna()
    interval_days = deltas.dt.total_seconds() / 86400.0

    # Remove invalid intervals (must be > 0)
    interval_days = interval_days[interval_days > 0].values

    date_range_start = df['timestamp'].iloc[0].strftime('%Y-%m-%d')
    date_range_end = df['timestamp'].iloc[-1].strftime('%Y-%m-%d')

    print(f"  Loaded {len(df)} records")
    print(f"  Valid intervals: {len(interval_days)}")
    print(f"  Date range: {date_range_start} to {date_range_end}")

    return interval_days, len(df), date_range_start, date_range_end


def interval_statistics(intervals):
    """Calculate basic descriptive statistics for intervals."""
    return {
        "sample_size": len(intervals),
        "min_days": round(float(np.min(intervals)), 6),
        "max_days": round(float(np.max(intervals)), 6),
        "mean_days": round(float(np.mean(intervals)), 6),
        "median_days": round(float(np.median(intervals)), 6),
        "std_dev": round(float(np.std(intervals, ddof=1)), 6),
        "q1_days": round(float(np.percentile(intervals, 25)), 6),
        "q3_days": round(float(np.percentile(intervals, 75)), 6),
        "iqr_days": round(float(np.percentile(intervals, 75) - np.percentile(intervals, 25)), 6)
    }


def chi_square_log_bins(intervals, n_bins=N_BINS):
    """Chi-square uniformity test on log10-binned intervals."""
    log_intervals = np.log10(intervals)
    min_log = log_intervals.min()
    max_log = log_intervals.max()
    bin_edges = np.linspace(min_log, max_log, n_bins + 1)

    bin_indices = np.digitize(log_intervals, bin_edges[1:-1], right=False)
    counts = np.bincount(bin_indices, minlength=n_bins)[:n_bins]

    n = counts.sum()
    expected = np.full_like(counts, n / n_bins, dtype=float)
    stat, p_value = stats.chisquare(counts, f_exp=expected)
    dof = n_bins - 1

    # Cramer's V
    v = float(np.sqrt(stat / (n * (n_bins - 1))))

    return {
        "chi_square": {
            "statistic": round(float(stat), 4),
            "p_value": float(p_value),
            "degrees_of_freedom": dof,
            "interpretation": "significant" if p_value < 0.05 else "not significant"
        },
        "cramers_v": round(v, 6),
        "bin_counts": counts.tolist()
    }


def ks_exponential_test(intervals):
    """KS test against exponential distribution (Poisson process baseline)."""
    mean_interval = np.mean(intervals)
    lam = 1.0 / mean_interval
    stat, p_value = stats.kstest(intervals, 'expon', args=(0, mean_interval))
    return {
        "ks_statistic": round(float(stat), 6),
        "ks_p_value": float(p_value),
        "lambda_parameter": round(float(lam), 6),
        "interpretation": "consistent with random" if p_value > 0.05 else "deviates from random"
    }


def clustering_analysis(intervals):
    """Coefficient of variation and clustering indicators."""
    mean_val = np.mean(intervals)
    std_val = np.std(intervals, ddof=1)
    cv = std_val / mean_val
    median_val = np.median(intervals)

    if cv > 1.5:
        cv_interp = "clustering"
    elif cv < 0.7:
        cv_interp = "regular"
    else:
        cv_interp = "random"

    intervals_lt_median = int(np.sum(intervals < median_val))
    intervals_gt_3x_mean = int(np.sum(intervals > 3 * mean_val))
    proportion_short = round(float(intervals_lt_median / len(intervals)), 6)

    return {
        "coefficient_of_variation": round(float(cv), 6),
        "cv_interpretation": cv_interp,
        "max_min_ratio": round(float(np.max(intervals) / np.min(intervals)), 4),
        "clustering_indicators": {
            "intervals_less_than_median": intervals_lt_median,
            "intervals_greater_than_3x_mean": intervals_gt_3x_mean,
            "proportion_short_intervals": proportion_short
        }
    }


def main():
    print("Case 2: Inter-Event Interval Analysis (Blind Study)")
    print("=" * 55)

    intervals, total_records, date_start, date_end = load_and_preprocess()

    ist = interval_statistics(intervals)
    print(f"\n  Interval stats: mean={ist['mean_days']:.4f} days, "
          f"median={ist['median_days']:.4f} days, CV={ist['std_dev']/ist['mean_days']:.4f}")

    uniformity = chi_square_log_bins(intervals)
    chi = uniformity['chi_square']
    print(f"\n  Chi-square (log-binned): X2={chi['statistic']}, p={chi['p_value']:.6e}, {chi['interpretation']}")
    print(f"  Cramer's V: {uniformity['cramers_v']}")

    exp_test = ks_exponential_test(intervals)
    print(f"\n  KS test (exponential): D={exp_test['ks_statistic']}, p={exp_test['ks_p_value']:.6e}, {exp_test['interpretation']}")

    clust = clustering_analysis(intervals)
    print(f"\n  CV: {clust['coefficient_of_variation']} ({clust['cv_interpretation']})")
    print(f"  Max/min ratio: {clust['max_min_ratio']}")

    results = {
        "data_processing": {
            "total_records_loaded": total_records,
            "valid_intervals_calculated": len(intervals),
            "date_range_start": date_start,
            "date_range_end": date_end,
            "timestamp_parsing_status": "success"
        },
        "interval_statistics": ist,
        "uniformity_test": uniformity,
        "exponential_baseline_test": exp_test,
        "clustering_analysis": clust
    }

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults written to {OUTPUT_PATH}")


if __name__ == '__main__':
    main()
