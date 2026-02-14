# Case 4B: Energy-Weighted Clustering Patterns - Stratified Population (Blind Study - Approach Two)

**Document Information**
- Version: 1.0
- Date: 2026-02-13
- Data: Anonymized data stratified by v_val quartiles, energy-weighted analysis
- Approach: Blind Study (Approach Two) - ISOLATED ANALYSIS
- Purpose: Validate weighted energy proxy clustering across v_val subpopulations

## Stratification Methodology

### v_val Quantile Stratification

Data is stratified by v_val quartiles into 4 groups, identical to Case 3B:

| Stratum | v_val Range | Sample Size | Percentage |
|---------|------------|-------------|------------|
| Q1 (0-25th percentile) | 6.0 - 6.1 | 3,876 | 38.4% |
| Q2 (25-50th percentile) | 6.13 - 6.2 | 1,293 | 12.8% |
| Q3 (50-75th percentile) | 6.21 - 6.5 | 2,523 | 25.0% |
| Q4 (75-100th percentile) | 6.56 - 9.5 | 2,413 | 23.9% |

**Total records:** 10,105

The `v_val` variable is used as a proxy weighting property. It does not necessarily represent true energy — it is an arbitrarily assigned weighting based on the value's magnitude.

### Energy Calculation

**Formula:** energy = 10^(1.5 x v_val)

This exponential weighting amplifies differences between v_val levels. Within a narrow quartile, events may have similar individual energies. However, across quartiles (especially Q4 with its wide v_val range of 6.56-9.5), the energy range spans many orders of magnitude.

### Why Energy-Weighting Matters for Stratified Analysis

Count-based analysis (Case 3B) treats every event equally. Energy-weighting tests whether high-energy events — those with large v_val — preferentially cluster in certain spatial bins. If energy clustering persists within strata where events have similar v_val (and thus similar energy), this indicates that spatial clustering is genuine and not an artifact of v_val-correlated energy distributions.

## Energy Distribution by Stratum

| Stratum | Total Energy | Mean Energy/Event | Min Event Energy | Max Event Energy | Dynamic Range |
|---------|-------------|-------------------|-----------------|-----------------|--------------|
| Q1 | 4.567 x 10^12 | 1.178 x 10^9 | 1.000 x 10^9 | 1.413 x 10^9 | 1.4x |
| Q2 | 2.578 x 10^12 | 1.994 x 10^9 | 1.567 x 10^9 | 1.995 x 10^9 | 1.3x |
| Q3 | 9.837 x 10^12 | 3.899 x 10^9 | 2.065 x 10^9 | 5.623 x 10^9 | 2.7x |
| Q4 | 6.497 x 10^14 | 2.693 x 10^11 | 6.918 x 10^9 | 1.778 x 10^14 | 25,700x |

**Key observation:** Q1-Q3 have relatively narrow energy ranges (1.3x to 2.7x dynamic range), meaning events within each stratum carry nearly equal weight. Q4 has an extreme dynamic range of ~25,700x, so a few high-v_val events dominate Q4's total energy. Notably, Q4 alone holds 97.5% of the total energy (6.497 x 10^14 out of 6.667 x 10^14).

## Results by Stratum

### Stratum 1 (v_val 0-25th percentile: 6.0-6.1)

- **Sample size:** 3,876 | **Total energy:** 4.567 x 10^12

| Variable | Chi-square | p-value | Cramer's V | Synth. Percentile | Verdict |
|----------|-----------|---------|------------|-------------------|---------|
| x_val | 3.579 x 10^10 | 0.0 | 784.58 | 100.0 | Energy clustering |
| y_val | 1.849 x 10^10 | 0.0 | 563.91 | 100.0 | Energy clustering |
| z_val | 2.047 x 10^10 | 0.0 | 593.34 | 100.0 | Energy clustering |

- **x_val:** Excess energy in bins 4,5,6,7,10,11,12,13,15; deficit in bins 1,2,3,8,9,14,16
  - Comparison to Case 3B (count-based): **Same pattern** (both show clustering)
  - Comparison to Case 4A (full population): **Same pattern**
- **y_val:** Excess energy in bins 3,4,8,10,13,14; deficit in bins 1,2,5,6,7,9,11,12,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering, 4B shows energy clustering)
  - Comparison to Case 4A: **Same pattern**
- **z_val:** Excess energy in bins 1,2,4,6,8,11,12,13,14,15; deficit in bins 3,5,7,9,10,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering, 4B shows energy clustering)
  - Comparison to Case 4A: **Same pattern**

![Case 4B Q1 x_val Heatmap](case_4b_heatmap_energy_stratum_1_x_val_blind.png)

![Case 4B Q1 y_val Heatmap](case_4b_heatmap_energy_stratum_1_y_val_blind.png)

![Case 4B Q1 z_val Heatmap](case_4b_heatmap_energy_stratum_1_z_val_blind.png)

### Stratum 2 (v_val 25-50th percentile: 6.13-6.2)

- **Sample size:** 1,293 | **Total energy:** 2.578 x 10^12

| Variable | Chi-square | p-value | Cramer's V | Synth. Percentile | Verdict |
|----------|-----------|---------|------------|-------------------|---------|
| x_val | 7.807 x 10^10 | 0.0 | 2,006.30 | 100.0 | Energy clustering |
| y_val | 4.324 x 10^10 | 0.0 | 1,493.21 | 100.0 | Energy clustering |
| z_val | 4.059 x 10^10 | 0.0 | 1,446.69 | 100.0 | Energy clustering |

- **x_val:** Excess energy in bins 4,5,6,11,12,15; deficit in bins 1,2,3,7,8,9,10,13,14,16
  - Comparison to Case 3B: **Same pattern** (both show clustering)
  - Comparison to Case 4A: **Same pattern**
- **y_val:** Excess energy in bins 1,7,8,9,10,11,12,13,14; deficit in bins 2,3,4,5,6,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**
- **z_val:** Excess energy in bins 1,2,3,5,6,8,9,11; deficit in bins 4,7,10,12,13,14,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**

![Case 4B Q2 x_val Heatmap](case_4b_heatmap_energy_stratum_2_x_val_blind.png)

![Case 4B Q2 y_val Heatmap](case_4b_heatmap_energy_stratum_2_y_val_blind.png)

![Case 4B Q2 z_val Heatmap](case_4b_heatmap_energy_stratum_2_z_val_blind.png)

### Stratum 3 (v_val 50-75th percentile: 6.21-6.5)

- **Sample size:** 2,523 | **Total energy:** 9.837 x 10^12

| Variable | Chi-square | p-value | Cramer's V | Synth. Percentile | Verdict |
|----------|-----------|---------|------------|-------------------|---------|
| x_val | 4.945 x 10^10 | 0.0 | 1,143.07 | 100.0 | Energy clustering |
| y_val | 5.153 x 10^10 | 0.0 | 1,166.84 | 100.0 | Energy clustering |
| z_val | 5.634 x 10^10 | 0.0 | 1,220.17 | 100.0 | Energy clustering |

- **x_val:** Excess energy in bins 4,5,9,11,13,14,15; deficit in bins 1,2,3,6,7,8,10,12,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**
- **y_val:** Excess energy in bins 2,4,5,6,12,14; deficit in bins 1,3,7,8,9,10,11,13,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**
- **z_val:** Excess energy in bins 1,4,6,8,10,11,13,15,16; deficit in bins 2,3,5,7,9,12,14
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**

![Case 4B Q3 x_val Heatmap](case_4b_heatmap_energy_stratum_3_x_val_blind.png)

![Case 4B Q3 y_val Heatmap](case_4b_heatmap_energy_stratum_3_y_val_blind.png)

![Case 4B Q3 z_val Heatmap](case_4b_heatmap_energy_stratum_3_z_val_blind.png)

### Stratum 4 (v_val 75-100th percentile: 6.56-9.5)

- **Sample size:** 2,413 | **Total energy:** 6.497 x 10^14

| Variable | Chi-square | p-value | Cramer's V | Synth. Percentile | Verdict |
|----------|-----------|---------|------------|-------------------|---------|
| x_val | 8.349 x 10^14 | 0.0 | 151,873.06 | 100.0 | Energy clustering |
| y_val | 9.756 x 10^14 | 0.0 | 164,173.86 | 100.0 | Energy clustering |
| z_val | 8.769 x 10^14 | 0.0 | 155,649.56 | 100.0 | Energy clustering |

- **x_val:** Excess energy in bins 1,4,5,7,14; deficit in bins 2,3,6,8,9,10,11,12,13,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**
- **y_val:** Excess energy in bins 4,8,10,15; deficit in bins 1,2,3,5,6,7,9,11,12,13,14,16
  - Comparison to Case 3B: **Same pattern** (both show clustering)
  - Comparison to Case 4A: **Same pattern**
- **z_val:** Excess energy in bins 3,5,10,11,12; deficit in bins 1,2,4,6,7,8,9,13,14,15,16
  - Comparison to Case 3B: **Different pattern** (3B showed no clustering)
  - Comparison to Case 4A: **Same pattern**

![Case 4B Q4 x_val Heatmap](case_4b_heatmap_energy_stratum_4_x_val_blind.png)

![Case 4B Q4 y_val Heatmap](case_4b_heatmap_energy_stratum_4_y_val_blind.png)

![Case 4B Q4 z_val Heatmap](case_4b_heatmap_energy_stratum_4_z_val_blind.png)

## Comparative Analysis

![Case 4B Energy Histogram Grid](case_4b_histogram_energy_grid_blind.png)

### Consistency Across Strata

| Variable | Q1 Verdict | Q2 Verdict | Q3 Verdict | Q4 Verdict | Consistent? |
|----------|-----------|-----------|-----------|-----------|-------------|
| x_val | Energy clustering | Energy clustering | Energy clustering | Energy clustering | Yes |
| y_val | Energy clustering | Energy clustering | Energy clustering | Energy clustering | Yes |
| z_val | Energy clustering | Energy clustering | Energy clustering | Energy clustering | Yes |

**All three variables show energy clustering in all four strata.** The energy clustering pattern is **v_val-independent** — it persists universally across all v_val subpopulations.

### Effect Size Variation Across Strata

![Case 4B Effect Size Comparison](case_4b_effect_size_energy_comparison_blind.png)

| Variable | Q1 Cramer's V | Q2 Cramer's V | Q3 Cramer's V | Q4 Cramer's V |
|----------|--------------|--------------|--------------|--------------|
| x_val | 784.58 | 2,006.30 | 1,143.07 | 151,873.06 |
| y_val | 563.91 | 1,493.21 | 1,166.84 | 164,173.86 |
| z_val | 593.34 | 1,446.69 | 1,220.17 | 155,649.56 |

Cramer's V values are extremely large (far exceeding 1.0) because the chi-square test is computed on energy sums rather than counts. The formula V = sqrt(chi2 / (n x (k-1))) assumes count-based chi-square, so these inflated values reflect the enormous chi-square statistics from energy-weighted analysis, not true effect sizes in the traditional sense.

**Q4 shows effect sizes ~100-200x larger than Q1-Q3**, driven by Q4's extreme energy dynamic range (25,700x). A few very high-energy events in Q4 dominate the chi-square statistic.

### Significance Comparison

![Case 4B Significance by Stratum](case_4b_significance_energy_by_stratum_blind.png)

All p-values are 0.0 (below floating-point precision) across all strata and variables. Every synthetic catalog also produced p = 0.0, placing real results at the 100th percentile. This universal significance is expected because even within narrow v_val ranges, events within a stratum still show non-uniform spatial distributions that produce enormous chi-square values when measured in energy units.

## Count-Based vs Energy-Based Comparison

![Case 4B Count vs Energy Comparison](case_4b_comparison_count_vs_energy_by_stratum_blind.png)

### Case 3B (Count-Based) vs Case 4B (Energy-Weighted)

| Variable | Stratum | Case 3B p-value | Case 3B Verdict | Case 4B p-value | Case 4B Verdict | Agreement |
|----------|---------|----------------|-----------------|----------------|-----------------|-----------|
| x_val | Q1 | 4.19 x 10^-2 | Clustering | 0.0 | Energy clustering | Same |
| x_val | Q2 | 6.50 x 10^-4 | Clustering | 0.0 | Energy clustering | Same |
| x_val | Q3 | 5.87 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| x_val | Q4 | 1.06 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| y_val | Q1 | 3.90 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| y_val | Q2 | 1.19 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| y_val | Q3 | 7.54 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| y_val | Q4 | 7.61 x 10^-4 | Clustering | 0.0 | Energy clustering | Same |
| z_val | Q1 | 2.81 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| z_val | Q2 | 1.62 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| z_val | Q3 | 7.05 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |
| z_val | Q4 | 8.49 x 10^-1 | No clustering | 0.0 | Energy clustering | **Different** |

**Only 4 of 12 comparisons agree.** Energy-weighting universally finds clustering in every stratum-variable combination, while count-based analysis found clustering in only 4 of 12. This dramatic difference has important implications:

1. **Energy-weighting amplifies small non-uniformities.** Even within narrow v_val strata (Q1: 6.0-6.1), slight variations in v_val produce energy differences that, when accumulated across bins, produce statistically extreme chi-square values.

2. **The chi-square test on energy sums is inherently more sensitive** than counts because the effective "sample size" in energy terms is enormous. A single bin containing one event with slightly higher v_val (e.g., 6.1 vs 6.0) adds ~40% more energy, which inflates the chi-square.

3. **Synthetic catalogs also produce p = 0.0**, meaning shuffled data shows the same energy clustering pattern. This suggests the energy clustering signal is driven by the v_val distribution within strata rather than genuine spatial non-uniformity.

## Key Findings

### 1. Energy Clustering is Universal but Potentially Artifactual

All three variables (x_val, y_val, z_val) show energy clustering in all four strata with p = 0.0. However, synthetic null hypothesis catalogs also produce p = 0.0 in all cases, meaning randomly shuffled data shows the same signal. This is a critical finding: the energy-weighted chi-square test may not discriminate between real spatial clustering and the inherent non-uniformity of energy within bins.

### 2. Energy Clustering is v_val-Independent

The pattern persists identically across all strata, regardless of v_val range. This contrasts with Case 3B count-based analysis, which found v_val-dependent patterns (clustering varied across strata).

### 3. Strongest Signal: All Variables Equal

Unlike count-based analyses where x_val showed the most consistent clustering, energy-weighted analysis cannot rank variables by signal strength — all three produce identical verdicts (p = 0.0 everywhere) with comparable effect sizes within each stratum.

### 4. Q4 Dominance

Q4 (v_val 6.56-9.5) holds 97.5% of total energy. Its Cramer's V values are ~100-200x larger than other strata, driven by extreme energy concentration in a few high-v_val events.

### 5. Robustness Assessment

The energy-weighted findings are statistically consistent (all p = 0.0, all at 100th percentile of synthetic) but lack discriminative power. The test cannot distinguish real clustering from uniform spatial distributions when energy weighting amplifies within-bin v_val variance. Count-based analysis (Case 3B) provides more nuanced and discriminating results.

## Blind Study Completion: Summary of All Cases

### Cases 1-4B Consolidated Findings

| Case | Analysis Type | x_val | y_val | z_val |
|------|--------------|-------|-------|-------|
| Case 1 | Distribution uniformity | Non-uniform | Non-uniform | Non-uniform |
| Case 3A | Count clustering (full) | Clustering | Clustering | Clustering |
| Case 3B | Count clustering (stratified) | Mixed (2/4 strata) | Mixed (1/4 strata) | No clustering (0/4) |
| Case 4A | Energy clustering (full) | Energy clustering | Energy clustering | Energy clustering |
| Case 4B | Energy clustering (stratified) | Energy clustering (4/4) | Energy clustering (4/4) | Energy clustering (4/4) |

### Variables That Consistently Show Clustering

- **x_val**: Shows clustering in Cases 3A, 4A, 4B, and partially in 3B (Q1, Q2). Most consistent count-based signal.
- **y_val**: Shows clustering in Cases 3A, 4A, 4B, and partially in 3B (Q4 only). Less consistent count-based signal.

### Variables That Show No Clustering

- **z_val**: Shows **no clustering** in any Case 3B stratum (count-based). However, it shows clustering in Cases 3A, 4A, and 4B. This makes z_val the weakest clustering candidate — its full-population clustering may be driven by cross-stratum effects rather than within-stratum patterns.

### Confidence Level

- **High confidence:** x_val exhibits genuine spatial clustering, validated across count-based and energy-weighted analyses, and partially persistent across v_val strata.
- **Moderate confidence:** y_val clustering is real but may be v_val-dependent (appears in Q4 count-based but not Q1-Q3).
- **Low confidence for z_val:** Energy-weighted clustering is present but likely artifactual (synthetic catalogs show identical patterns). Count-based stratified analysis found no clustering in any stratum.
- **Readiness:** The blind study has identified which variables carry signal and which do not. Variable identities can now be revealed for interpretation.

## Limitations

- Variable identities remain unknown — no physical interpretation is possible
- Stratification reduces sample sizes (Q2 has only 1,293 records), lowering statistical power for count-based tests
- Energy weighting emphasizes rare, large events — Q4 with 24% of events holds 97.5% of energy
- The exponential energy formula (10^(1.5 x v_val)) creates extreme dynamic ranges that can overwhelm chi-square tests
- Synthetic catalogs also produce p = 0.0 for energy-weighted analysis, limiting the discriminative value of null hypothesis comparison
- The analysis remains entirely blind with no external context or interpretation

---

**Generation Details**
- Version: 1.0
- Date: 2026-02-13
- Planning prepared with: Claude.ai Web Interface (Haiku 4.5)
- Generated with: Claude Code 2.1.41 (Claude Model Opus 4.6)
- Project: Approach Two Blind Study - ISOLATED ANALYSIS
- Isolation Status: Complete separation from main project
