"""
Case 4B: Test Suite - Energy-Weighted Stratified Clustering (Blind Study - Approach Two)
Validates energy-weighted stratified clustering analysis results including strata creation,
energy calculations, chi-square tests, Cramér's V, and synthetic null hypothesis catalogs.
"""

import json
import os
import numpy as np
import pytest

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4b_results_blind.json')

VARIABLES = ['x_val', 'y_val', 'z_val']
STRATUM_NUMS = ['stratum_1', 'stratum_2', 'stratum_3', 'stratum_4']
N_BINS = 16
ALPHA = 0.05
N_SYNTHETIC = 100


@pytest.fixture(scope='module')
def results():
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


class TestCase4BStructure:
    """Verify result structure and completeness."""

    def test_four_strata_present(self, results):
        for s_num in STRATUM_NUMS:
            assert s_num in results, f"Missing stratum: {s_num}"

    def test_stratification_metadata(self, results):
        assert results['stratification'] == "v_val quartiles (4 groups)"
        assert 'total_sample_size' in results
        assert 'stratum_sizes' in results
        assert 'stratum_total_energies' in results
        assert 'comparative_summary' in results

    def test_energy_calculation_documented(self, results):
        assert results['energy_calculation'] == "energy = 10^(1.5 * v_val)"

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
            assert 'total_energy' in results[s_num]
            assert 'mean_energy_per_event' in results[s_num]


class TestCase4BEnergyCalculations:
    """Verify energy calculations produce positive values."""

    def test_stratum_energies_positive(self, results):
        for s_num in STRATUM_NUMS:
            assert results[s_num]['total_energy'] > 0, \
                f"{s_num} total energy must be > 0"

    def test_stratum_total_energies_match(self, results):
        for s_num, s_label in zip(STRATUM_NUMS,
                                   ['group_1_0_25pct', 'group_2_25_50pct',
                                    'group_3_50_75pct', 'group_4_75_100pct']):
            stratum_energy = results[s_num]['total_energy']
            summary_energy = results['stratum_total_energies'][s_label]
            assert abs(stratum_energy - summary_energy) / max(stratum_energy, 1) < 0.01, \
                f"{s_num} energy mismatch: {stratum_energy} vs {summary_energy}"

    def test_mean_energy_consistent(self, results):
        for s_num in STRATUM_NUMS:
            total = results[s_num]['total_energy']
            n = results[s_num]['sample_size']
            mean = results[s_num]['mean_energy_per_event']
            expected_mean = total / n
            assert abs(mean - expected_mean) / max(expected_mean, 1) < 0.01


class TestCase4BStrataSizes:
    """Verify strata have sufficient sample sizes."""

    def test_each_stratum_above_50(self, results):
        for s_num in STRATUM_NUMS:
            n = results[s_num]['sample_size']
            assert n > 50, f"{s_num} has only {n} records (< 50)"

    def test_strata_sum_to_total(self, results):
        total = sum(results[s_num]['sample_size'] for s_num in STRATUM_NUMS)
        assert total == results['total_sample_size'], \
            f"Strata sum {total} != total {results['total_sample_size']}"


class TestCase4BEnergyPerBin:
    """Validate energy per bin sums to stratum total energy."""

    def test_energy_per_bin_sums_to_stratum_total(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                energy_sum = sum(results[s_num][var]['energy_per_bin'])
                total = results[s_num][var]['total_energy']
                assert abs(energy_sum - total) / max(total, 1) < 0.01, \
                    f"{s_num}/{var}: energy per bin sum {energy_sum:.4e} != total {total:.4e}"

    def test_sixteen_bins(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                assert len(results[s_num][var]['energy_per_bin']) == N_BINS

    def test_all_bin_energies_non_negative(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                for i, e in enumerate(results[s_num][var]['energy_per_bin']):
                    assert e >= 0, f"{s_num}/{var} bin {i+1} has negative energy: {e}"


class TestCase4BChiSquare:
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
                    assert verdict == "energy clustering", \
                        f"{s_num}/{var}: p={p} < {ALPHA} but verdict='{verdict}'"
                else:
                    assert verdict == "no energy clustering", \
                        f"{s_num}/{var}: p={p} >= {ALPHA} but verdict='{verdict}'"


class TestCase4BCramersV:
    """Validate Cramér's V calculations."""

    def test_cramers_v_non_negative(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                v = results[s_num][var]['cramers_v']
                assert v >= 0, f"{s_num}/{var} Cramér's V is negative: {v}"

    def test_cramers_v_computed_correctly(self, results):
        for s_num in STRATUM_NUMS:
            for var in VARIABLES:
                chi2 = results[s_num][var]['chi_square']
                n = results[s_num]['sample_size']
                expected_v = np.sqrt(chi2 / (n * (N_BINS - 1)))
                actual_v = results[s_num][var]['cramers_v']
                assert abs(actual_v - expected_v) < 1e-4, \
                    f"{s_num}/{var}: V={actual_v} != expected {expected_v:.6f}"


class TestCase4BSyntheticCatalogs:
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


class TestCase4BComparativeSummary:
    """Validate the comparative summary."""

    def test_consistency_flags_present(self, results):
        comp = results['comparative_summary']
        for var in VARIABLES:
            assert f"{var}_consistent_across_strata" in comp

    def test_interpretation_present(self, results):
        assert 'interpretation' in results['comparative_summary']

    def test_energy_pattern_dependency_flag(self, results):
        assert 'energy_pattern_v_val_dependent' in results['comparative_summary']
