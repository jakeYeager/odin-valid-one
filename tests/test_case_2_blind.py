"""
Case 2: Test Suite - Blind Study (Approach Two)
Validates inter-event interval analysis results: statistics, chi-square,
KS test, and clustering indicators.
"""

import json
import os
import numpy as np
import pytest

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_2_results_blind.json')

N_BINS = 16
ALPHA = 0.05


@pytest.fixture(scope='module')
def results():
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


class TestCase2Structure:
    """Verify result structure and completeness."""

    def test_top_level_keys(self, results):
        required = ['data_processing', 'interval_statistics',
                     'uniformity_test', 'exponential_baseline_test',
                     'clustering_analysis']
        for key in required:
            assert key in results, f"Missing top-level key: {key}"

    def test_data_processing_keys(self, results):
        dp = results['data_processing']
        for key in ['total_records_loaded', 'valid_intervals_calculated',
                     'date_range_start', 'date_range_end', 'timestamp_parsing_status']:
            assert key in dp, f"data_processing missing: {key}"

    def test_interval_statistics_keys(self, results):
        ist = results['interval_statistics']
        for key in ['sample_size', 'min_days', 'max_days', 'mean_days',
                     'median_days', 'std_dev', 'q1_days', 'q3_days', 'iqr_days']:
            assert key in ist, f"interval_statistics missing: {key}"

    def test_uniformity_test_keys(self, results):
        ut = results['uniformity_test']
        assert 'chi_square' in ut
        assert 'cramers_v' in ut
        assert 'bin_counts' in ut
        for key in ['statistic', 'p_value', 'degrees_of_freedom', 'interpretation']:
            assert key in ut['chi_square'], f"chi_square missing: {key}"

    def test_exponential_test_keys(self, results):
        et = results['exponential_baseline_test']
        for key in ['ks_statistic', 'ks_p_value', 'lambda_parameter', 'interpretation']:
            assert key in et, f"exponential_baseline_test missing: {key}"

    def test_clustering_keys(self, results):
        ca = results['clustering_analysis']
        for key in ['coefficient_of_variation', 'cv_interpretation',
                     'max_min_ratio', 'clustering_indicators']:
            assert key in ca, f"clustering_analysis missing: {key}"
        ci = ca['clustering_indicators']
        for key in ['intervals_less_than_median', 'intervals_greater_than_3x_mean',
                     'proportion_short_intervals']:
            assert key in ci, f"clustering_indicators missing: {key}"


class TestCase2DataProcessing:
    """Validate data processing results."""

    def test_records_loaded_positive(self, results):
        assert results['data_processing']['total_records_loaded'] > 100

    def test_valid_intervals_positive(self, results):
        assert results['data_processing']['valid_intervals_calculated'] > 100

    def test_intervals_less_than_records(self, results):
        dp = results['data_processing']
        assert dp['valid_intervals_calculated'] < dp['total_records_loaded']

    def test_parsing_success(self, results):
        assert results['data_processing']['timestamp_parsing_status'] == 'success'


class TestCase2IntervalStatistics:
    """Validate interval statistics."""

    def test_min_positive(self, results):
        assert results['interval_statistics']['min_days'] > 0

    def test_max_greater_than_min(self, results):
        ist = results['interval_statistics']
        assert ist['max_days'] > ist['min_days']

    def test_mean_positive(self, results):
        assert results['interval_statistics']['mean_days'] > 0

    def test_median_positive(self, results):
        assert results['interval_statistics']['median_days'] > 0

    def test_std_dev_positive(self, results):
        assert results['interval_statistics']['std_dev'] > 0

    def test_mean_between_min_and_max(self, results):
        ist = results['interval_statistics']
        assert ist['min_days'] <= ist['mean_days'] <= ist['max_days']

    def test_median_between_min_and_max(self, results):
        ist = results['interval_statistics']
        assert ist['min_days'] <= ist['median_days'] <= ist['max_days']

    def test_q1_less_than_q3(self, results):
        ist = results['interval_statistics']
        assert ist['q1_days'] <= ist['q3_days']

    def test_iqr_equals_q3_minus_q1(self, results):
        ist = results['interval_statistics']
        expected_iqr = ist['q3_days'] - ist['q1_days']
        assert abs(ist['iqr_days'] - expected_iqr) < 0.001

    def test_sample_size_matches(self, results):
        ist = results['interval_statistics']
        dp = results['data_processing']
        assert ist['sample_size'] == dp['valid_intervals_calculated']


class TestCase2ChiSquare:
    """Validate chi-square test on log-binned intervals."""

    def test_degrees_of_freedom(self, results):
        assert results['uniformity_test']['chi_square']['degrees_of_freedom'] == N_BINS - 1

    def test_p_value_range(self, results):
        p = results['uniformity_test']['chi_square']['p_value']
        assert 0 <= p <= 1, f"p-value out of range: {p}"

    def test_statistic_non_negative(self, results):
        assert results['uniformity_test']['chi_square']['statistic'] >= 0

    def test_interpretation_matches_p_value(self, results):
        chi = results['uniformity_test']['chi_square']
        if chi['p_value'] < ALPHA:
            assert chi['interpretation'] == "significant"
        else:
            assert chi['interpretation'] == "not significant"

    def test_sixteen_bins(self, results):
        assert len(results['uniformity_test']['bin_counts']) == N_BINS

    def test_bin_counts_sum(self, results):
        total = sum(results['uniformity_test']['bin_counts'])
        assert total == results['interval_statistics']['sample_size']

    def test_cramers_v_range(self, results):
        v = results['uniformity_test']['cramers_v']
        assert 0 <= v <= 1, f"Cramer's V out of range: {v}"

    def test_cramers_v_computed_correctly(self, results):
        chi2 = results['uniformity_test']['chi_square']['statistic']
        n = results['interval_statistics']['sample_size']
        expected_v = np.sqrt(chi2 / (n * (N_BINS - 1)))
        actual_v = results['uniformity_test']['cramers_v']
        assert abs(actual_v - expected_v) < 1e-4, \
            f"Cramer's V {actual_v} != expected {expected_v:.6f}"


class TestCase2KSTest:
    """Validate KS test against exponential distribution."""

    def test_ks_p_value_range(self, results):
        p = results['exponential_baseline_test']['ks_p_value']
        assert 0 <= p <= 1, f"KS p-value out of range: {p}"

    def test_ks_statistic_range(self, results):
        d = results['exponential_baseline_test']['ks_statistic']
        assert 0 <= d <= 1, f"KS statistic out of range: {d}"

    def test_lambda_positive(self, results):
        assert results['exponential_baseline_test']['lambda_parameter'] > 0

    def test_interpretation_matches_p_value(self, results):
        et = results['exponential_baseline_test']
        if et['ks_p_value'] > ALPHA:
            assert et['interpretation'] == "consistent with random"
        else:
            assert et['interpretation'] == "deviates from random"


class TestCase2Clustering:
    """Validate clustering analysis."""

    def test_cv_positive(self, results):
        assert results['clustering_analysis']['coefficient_of_variation'] > 0

    def test_cv_computed_correctly(self, results):
        ist = results['interval_statistics']
        expected_cv = ist['std_dev'] / ist['mean_days']
        actual_cv = results['clustering_analysis']['coefficient_of_variation']
        assert abs(actual_cv - expected_cv) < 0.001, \
            f"CV {actual_cv} != expected {expected_cv:.6f}"

    def test_cv_interpretation_valid(self, results):
        interp = results['clustering_analysis']['cv_interpretation']
        assert interp in ('clustering', 'random', 'regular')

    def test_max_min_ratio_positive(self, results):
        assert results['clustering_analysis']['max_min_ratio'] > 1

    def test_proportion_short_range(self, results):
        p = results['clustering_analysis']['clustering_indicators']['proportion_short_intervals']
        assert 0 < p < 1
