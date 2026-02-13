"""
Case 1: Test Suite - Blind Study (Approach Two)
Validates chi-square uniformity results, Cramer's V calculation,
and cross-variable comparison.
"""

import json
import os
import numpy as np
import pytest

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_1_results_blind.json')

VARIABLES = ['x_val', 'y_val', 'z_val']
N_BINS = 16
ALPHA = 0.05


@pytest.fixture(scope='module')
def results():
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


class TestCase1Structure:
    """Verify result structure and completeness."""

    def test_all_variables_present(self, results):
        for var in VARIABLES:
            assert var in results, f"Missing variable: {var}"

    def test_required_keys(self, results):
        required = ['chi_square', 'rayleigh', 'effect_size_cramers_v',
                     'sample_size', 'bin_counts', 'expected_count_per_bin']
        for var in VARIABLES:
            for key in required:
                assert key in results[var], f"{var} missing key: {key}"

    def test_chi_square_keys(self, results):
        chi_keys = ['statistic', 'p_value', 'degrees_of_freedom', 'interpretation']
        for var in VARIABLES:
            for key in chi_keys:
                assert key in results[var]['chi_square'], f"{var} chi_square missing: {key}"

    def test_rayleigh_keys(self, results):
        for var in VARIABLES:
            assert 'statistic' in results[var]['rayleigh']
            assert 'p_value' in results[var]['rayleigh']


class TestCase1SampleSize:
    """Verify sample sizes are valid."""

    def test_sample_size_positive(self, results):
        for var in VARIABLES:
            assert results[var]['sample_size'] > 0, f"{var} has zero sample size"

    def test_sample_sizes_consistent(self, results):
        sizes = [results[var]['sample_size'] for var in VARIABLES]
        assert len(set(sizes)) == 1, f"Sample sizes differ across variables: {sizes}"

    def test_bin_counts_sum_to_sample_size(self, results):
        for var in VARIABLES:
            total = sum(results[var]['bin_counts'])
            assert total == results[var]['sample_size'], \
                f"{var}: bin counts sum {total} != sample size {results[var]['sample_size']}"

    def test_sixteen_bins(self, results):
        for var in VARIABLES:
            assert len(results[var]['bin_counts']) == N_BINS, \
                f"{var} has {len(results[var]['bin_counts'])} bins, expected {N_BINS}"


class TestCase1ChiSquare:
    """Validate chi-square test results."""

    def test_degrees_of_freedom(self, results):
        for var in VARIABLES:
            assert results[var]['chi_square']['degrees_of_freedom'] == N_BINS - 1

    def test_p_value_range(self, results):
        for var in VARIABLES:
            p = results[var]['chi_square']['p_value']
            assert 0 <= p <= 1, f"{var} p-value out of range: {p}"

    def test_statistic_non_negative(self, results):
        for var in VARIABLES:
            assert results[var]['chi_square']['statistic'] >= 0

    def test_interpretation_matches_p_value(self, results):
        for var in VARIABLES:
            p = results[var]['chi_square']['p_value']
            interp = results[var]['chi_square']['interpretation']
            if p < ALPHA:
                assert interp == "significant", \
                    f"{var}: p={p} < {ALPHA} but interpretation is '{interp}'"
            else:
                assert interp == "not significant", \
                    f"{var}: p={p} >= {ALPHA} but interpretation is '{interp}'"


class TestCase1CramersV:
    """Validate Cramer's V effect size calculation."""

    def test_cramers_v_range(self, results):
        for var in VARIABLES:
            v = results[var]['effect_size_cramers_v']
            assert 0 <= v <= 1, f"{var} Cramer's V out of range: {v}"

    def test_cramers_v_computed_correctly(self, results):
        for var in VARIABLES:
            chi2 = results[var]['chi_square']['statistic']
            n = results[var]['sample_size']
            k = N_BINS
            expected_v = np.sqrt(chi2 / (n * (k - 1)))
            actual_v = results[var]['effect_size_cramers_v']
            assert abs(actual_v - expected_v) < 1e-4, \
                f"{var}: Cramer's V {actual_v} != expected {expected_v:.6f}"


class TestCase1Rayleigh:
    """Validate Rayleigh test results."""

    def test_rayleigh_statistic_non_negative(self, results):
        for var in VARIABLES:
            assert results[var]['rayleigh']['statistic'] >= 0

    def test_rayleigh_p_value_range(self, results):
        for var in VARIABLES:
            p = results[var]['rayleigh']['p_value']
            assert 0 <= p <= 1, f"{var} Rayleigh p-value out of range: {p}"


class TestCase1CrossVariable:
    """Compare results across variables."""

    def test_identify_significant_variables(self, results):
        """At least one variable should have a definitive result (sig or not)."""
        interpretations = [results[var]['chi_square']['interpretation'] for var in VARIABLES]
        assert all(i in ('significant', 'not significant') for i in interpretations)

    def test_effect_sizes_are_finite(self, results):
        for var in VARIABLES:
            v = results[var]['effect_size_cramers_v']
            assert np.isfinite(v), f"{var} has non-finite Cramer's V"

    def test_expected_count_calculation(self, results):
        for var in VARIABLES:
            n = results[var]['sample_size']
            expected = results[var]['expected_count_per_bin']
            assert abs(expected - n / N_BINS) < 0.1, \
                f"{var}: expected_count_per_bin {expected} != {n}/{N_BINS}"
