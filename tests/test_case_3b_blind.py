"""
Case 3B: Test Suite - Stratified Clustering Patterns (Blind Study - Approach Two)
Validates stratified clustering analysis results including strata creation,
chi-square tests, Cramér's V, and synthetic null hypothesis catalogs.
"""

import json
import os
import numpy as np
import pytest

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_3b_results_blind.json')

VARIABLES = ['x_val', 'y_val', 'z_val']
STRATUM_NUMS = ['stratum_1', 'stratum_2', 'stratum_3', 'stratum_4']
N_BINS = 16
ALPHA = 0.05
N_SYNTHETIC = 100


@pytest.fixture(scope='module')
def results():
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


class TestCase3BStructure:
    """Verify result structure and completeness."""

    def test_four_strata_present(self, results):
        for s_num in STRATUM_NUMS:
            assert s_num in results, f"Missing stratum: {s_num}"

    def test_stratification_metadata(self, results):
        assert 'stratification' in results
        assert 'total_sample_size' in results
        assert 'stratum_sizes' in results
        assert 'comparative_summary' in results

    def test_stratum_sizes_dict(self, results):
        sizes = results['stratum_sizes']
        assert len(sizes) == 4

    def test_variables_in_each_stratum(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert var in results[s_num], f"{s_num} missing variable: {var}"

    def test_stratum_metadata(self, results):
        for s_num in STRATUM_NUMS:
            assert 'v_val_range' in results[s_num]
            assert 'sample_size' in results[s_num]


class TestCase3BStrataSizes:
    """Verify strata have sufficient sample sizes."""

    def test_each_stratum_above_50(self, results):
        for s_num in STRATUM_NUMS:
            n = results[s_num]['sample_size']
            assert n > 50, f"{s_num} has only {n} records (< 50)"

    def test_strata_sum_to_total(self, results):
        total = sum(results[s_num]['sample_size'] for s_num in STRATUM_NUMS)
        assert total == results['total_sample_size'], \
            f"Strata sum {total} != total {results['total_sample_size']}"


class TestCase3BChiSquare:
    """Validate chi-square test results per stratum."""

    def test_p_value_range(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                p = results[s_num][var]['p_value']
                assert 0 <= p <= 1, f"{s_num}/{var} p-value out of range: {p}"

    def test_chi_square_non_negative(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert results[s_num][var]['chi_square'] >= 0

    def test_degrees_of_freedom(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert results[s_num][var]['degrees_of_freedom'] == N_BINS - 1

    def test_verdict_matches_p_value(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                p = results[s_num][var]['p_value']
                verdict = results[s_num][var]['verdict']
                if p < ALPHA:
                    assert verdict == "clustering", \
                        f"{s_num}/{var}: p={p} < {ALPHA} but verdict='{verdict}'"
                else:
                    assert verdict == "no clustering", \
                        f"{s_num}/{var}: p={p} >= {ALPHA} but verdict='{verdict}'"


class TestCase3BBinCounts:
    """Validate bin counts per stratum."""

    def test_bin_counts_sum_to_stratum_size(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                total = sum(results[s_num][var]['bin_counts'])
                expected = results[s_num]['sample_size']
                assert total == expected, \
                    f"{s_num}/{var}: bin counts sum {total} != stratum size {expected}"

    def test_sixteen_bins(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert len(results[s_num][var]['bin_counts']) == N_BINS


class TestCase3BCramersV:
    """Validate Cramér's V calculations."""

    def test_cramers_v_range(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                v = results[s_num][var]['cramers_v']
                assert 0 <= v <= 1, f"{s_num}/{var} Cramér's V out of range: {v}"

    def test_cramers_v_computed_correctly(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                chi2 = results[s_num][var]['chi_square']
                n = results[s_num]['sample_size']
                expected_v = np.sqrt(chi2 / (n * (N_BINS - 1)))
                actual_v = results[s_num][var]['cramers_v']
                assert abs(actual_v - expected_v) < 1e-4, \
                    f"{s_num}/{var}: V={actual_v} != expected {expected_v:.6f}"


class TestCase3BSyntheticCatalogs:
    """Validate synthetic null hypothesis catalogs per stratum."""

    def test_synthetic_percentile_present(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert 'synthetic_percentile' in results[s_num][var], \
                    f"{s_num}/{var} missing synthetic_percentile"

    def test_synthetic_percentile_range(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                pct = results[s_num][var]['synthetic_percentile']
                assert 0 <= pct <= 100, \
                    f"{s_num}/{var} synthetic percentile out of range: {pct}"

    def test_synthetic_p_values_generated(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                synth = results[s_num][var].get('synthetic_p_values', [])
                assert len(synth) == N_SYNTHETIC, \
                    f"{s_num}/{var}: {len(synth)} synthetic p-values, expected {N_SYNTHETIC}"

    def test_synthetic_p_values_valid(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                for p in results[s_num][var]['synthetic_p_values']:
                    assert 0 <= p <= 1

    def test_percentile_calculation_correct(self, results):
        """Verify percentile rank is consistent with synthetic p-values."""
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                real_p = results[s_num][var]['p_value']
                synth_p = np.array(results[s_num][var]['synthetic_p_values'])
                expected_pct = float(np.sum(synth_p <= real_p) / len(synth_p) * 100)
                actual_pct = results[s_num][var]['synthetic_percentile']
                assert abs(actual_pct - expected_pct) < 3.0, \
                    f"{s_num}/{var}: pct {actual_pct} != expected {expected_pct:.2f}"


class TestCase3BComparativeSummary:
    """Validate the comparative summary."""

    def test_consistency_flags_present(self, results):
        comp = results['comparative_summary']
        for var in VARIABLES:
            assert f"{var}_consistent" in comp

    def test_interpretation_present(self, results):
        assert 'interpretation' in results['comparative_summary']
