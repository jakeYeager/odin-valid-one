"""
Case 4A: Test Suite - Energy-Weighted Clustering (Blind Study - Approach Two)
Validates energy-weighted clustering analysis results including chi-square tests,
Cramér's V, Rayleigh tests, energy calculations, and synthetic null catalogs.
"""

import json
import os
import numpy as np
import pytest

RESULTS_PATH = os.path.join(os.path.dirname(__file__), '..', 'output', 'case_4a_results_blind.json')

VARIABLES = ['x_val', 'y_val', 'z_val']
N_BINS = 16
ALPHA = 0.05
N_SYNTHETIC = 1000


@pytest.fixture(scope='module')
def results():
    with open(RESULTS_PATH, 'r') as f:
        return json.load(f)


class TestCase4ASampleAndEnergy:
    """Verify sample size and energy calculations."""

    def test_sample_size_above_1000(self, results):
        assert results['sample_size'] > 1000, \
            f"Sample size {results['sample_size']} is not > 1000"

    def test_energy_calculation_positive(self, results):
        assert results['total_energy'] > 0, "Total energy must be > 0"

    def test_total_energy_present(self, results):
        assert 'total_energy' in results
        assert 'energy_calculation' in results
        assert results['energy_calculation'] == "energy = 10^(1.5 * v_val)"


class TestCase4AStructure:
    """Verify result structure and completeness."""

    def test_all_variables_present(self, results):
        for var in VARIABLES:
            assert var in results, f"Missing variable: {var}"

    def test_required_keys(self, results):
        required = ['chi_square_energy', 'rayleigh', 'cramers_v',
                     'energy_per_bin', 'expected_energy_per_bin',
                     'significant_bins_excess', 'significant_bins_deficit']
        for var in VARIABLES:
            for key in required:
                assert key in results[var], f"{var} missing key: {key}"

    def test_chi_square_energy_keys(self, results):
        chi_keys = ['statistic', 'p_value', 'degrees_of_freedom', 'interpretation']
        for var in VARIABLES:
            for key in chi_keys:
                assert key in results[var]['chi_square_energy'], \
                    f"{var} chi_square_energy missing: {key}"

    def test_rayleigh_keys(self, results):
        for var in VARIABLES:
            assert 'statistic' in results[var]['rayleigh']
            assert 'p_value' in results[var]['rayleigh']

    def test_synthetic_section_present(self, results):
        assert 'synthetic_null_hypothesis' in results


class TestCase4AEnergyPerBin:
    """Validate energy per bin calculations."""

    def test_energy_per_bin_sums_to_total(self, results):
        for var in VARIABLES:
            energy_sum = sum(results[var]['energy_per_bin'])
            total = results['total_energy']
            assert abs(energy_sum - total) / total < 0.01, \
                f"{var}: energy per bin sum {energy_sum:.4e} != total {total:.4e}"

    def test_sixteen_bins(self, results):
        for var in VARIABLES:
            assert len(results[var]['energy_per_bin']) == N_BINS, \
                f"{var} has {len(results[var]['energy_per_bin'])} bins, expected {N_BINS}"

    def test_all_bin_energies_non_negative(self, results):
        for var in VARIABLES:
            for i, e in enumerate(results[var]['energy_per_bin']):
                assert e >= 0, f"{var} bin {i+1} has negative energy: {e}"


class TestCase4AChiSquare:
    """Validate chi-square test results."""

    def test_degrees_of_freedom(self, results):
        for var in VARIABLES:
            assert results[var]['chi_square_energy']['degrees_of_freedom'] == N_BINS - 1

    def test_p_value_range(self, results):
        for var in VARIABLES:
            p = results[var]['chi_square_energy']['p_value']
            assert 0 <= p <= 1, f"{var} p-value out of range: {p}"

    def test_statistic_non_negative(self, results):
        for var in VARIABLES:
            assert results[var]['chi_square_energy']['statistic'] >= 0

    def test_interpretation_matches_p_value(self, results):
        for var in VARIABLES:
            p = results[var]['chi_square_energy']['p_value']
            interp = results[var]['chi_square_energy']['interpretation']
            if p < ALPHA:
                assert interp == "significant", \
                    f"{var}: p={p} < {ALPHA} but interpretation is '{interp}'"
            else:
                assert interp == "not significant", \
                    f"{var}: p={p} >= {ALPHA} but interpretation is '{interp}'"


class TestCase4ACramersV:
    """Validate Cramér's V effect size calculation."""

    def test_cramers_v_non_negative(self, results):
        """V >= 0 always. Note: V can exceed 1 when chi-square is computed
        on energy sums rather than counts, because the formula assumes
        count-based chi-square. This is expected with extreme energy ranges."""
        for var in VARIABLES:
            v = results[var]['cramers_v']
            assert v >= 0, f"{var} Cramér's V is negative: {v}"

    def test_cramers_v_computed_correctly(self, results):
        for var in VARIABLES:
            chi2 = results[var]['chi_square_energy']['statistic']
            n = results['sample_size']
            k = N_BINS
            expected_v = np.sqrt(chi2 / (n * (k - 1)))
            actual_v = results[var]['cramers_v']
            assert abs(actual_v - expected_v) < 1e-4, \
                f"{var}: Cramér's V {actual_v} != expected {expected_v:.6f}"


class TestCase4ARayleigh:
    """Validate Rayleigh test results."""

    def test_rayleigh_statistic_non_negative(self, results):
        for var in VARIABLES:
            assert results[var]['rayleigh']['statistic'] >= 0

    def test_rayleigh_p_value_range(self, results):
        for var in VARIABLES:
            p = results[var]['rayleigh']['p_value']
            assert 0 <= p <= 1, f"{var} Rayleigh p-value out of range: {p}"


class TestCase4ASyntheticCatalogs:
    """Validate synthetic null hypothesis catalogs."""

    def test_synthetic_catalogs_count(self, results):
        synth = results['synthetic_null_hypothesis']
        assert synth['synthetic_catalogs_generated'] == N_SYNTHETIC

    def test_energy_weighting_applied(self, results):
        synth = results['synthetic_null_hypothesis']
        assert synth['energy_weighting_applied'] is True

    def test_synthetic_p_values_populated(self, results):
        synth = results['synthetic_null_hypothesis']
        for var in VARIABLES:
            p_vals = synth[f'{var}_synthetic_p_values']
            assert len(p_vals) == N_SYNTHETIC, \
                f"{var} has {len(p_vals)} synthetic p-values, expected {N_SYNTHETIC}"

    def test_synthetic_p_values_valid(self, results):
        synth = results['synthetic_null_hypothesis']
        for var in VARIABLES:
            p_vals = synth[f'{var}_synthetic_p_values']
            for p in p_vals:
                assert 0 <= p <= 1, f"{var} synthetic p-value out of range: {p}"

    def test_percentile_rank_present(self, results):
        synth = results['synthetic_null_hypothesis']
        pct = synth['percentile_rank_analysis']
        for var in VARIABLES:
            key = f'{var}_real_p_percentile'
            assert key in pct, f"Missing percentile rank: {key}"

    def test_percentile_rank_range(self, results):
        synth = results['synthetic_null_hypothesis']
        pct = synth['percentile_rank_analysis']
        for var in VARIABLES:
            val = pct[f'{var}_real_p_percentile']
            assert 0 <= val <= 100, f"{var} percentile rank out of range: {val}"

    def test_percentile_rank_correct(self, results):
        """Verify percentile rank calculation is consistent with synthetic p-values."""
        synth = results['synthetic_null_hypothesis']
        pct = synth['percentile_rank_analysis']
        for var in VARIABLES:
            real_p = results[var]['chi_square_energy']['p_value']
            synthetic_p = np.array(synth[f'{var}_synthetic_p_values'])
            expected_pct = float(np.sum(synthetic_p <= real_p) / len(synthetic_p) * 100)
            actual_pct = pct[f'{var}_real_p_percentile']
            assert abs(actual_pct - expected_pct) < 0.15, \
                f"{var}: percentile {actual_pct} != expected {expected_pct:.2f}"
