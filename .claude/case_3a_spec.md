FIREWALL REMINDER: This is a blind study. You have no knowledge of what
the data represents or what patterns are expected. Analyze objectively 
for clustering without assumptions about distributions or mechanisms.

I have anonymized data in data/record_vals.csv with columns:
a_val, v_val, x_val, y_val, z_val (all numeric)

Cases 1-2B tested individual variable distributions and inter-event timing.
Now test whether x_val, y_val, and z_val show clustering patterns when 
analyzed across their full ranges using 16-bin uniformity testing.

This is the primary clustering detection case for the full population.

1. Create src/case_3a_blind_analysis.py that:
   
   a) Load data/record_vals.csv
      - Load all records (full population, no filtering)
      - Verify data integrity
   
   b) For EACH variable (x_val, y_val, z_val):
      
      i) Create 16 equal bins:
         - Bin size = max(variable) / 16
         - Bin 1: 0 to bin_size
         - Bin 2: bin_size to 2*bin_size
         - ... Bin 16: 15*bin_size to max(variable)
      
      ii) Count records in each bin:
         - Total records in dataset: N
         - Expected count per bin (uniform): N / 16
         - Actual count per bin: observed_count[i]
      
      iii) Run chi-square goodness-of-fit test:
         - Null hypothesis: records uniformly distributed across bins
         - Calculate χ² = sum((observed - expected)² / expected)
         - Calculate p-value (degrees of freedom = 15)
         - If p < 0.05: distribution is NOT uniform (clustering exists)
         - If p > 0.05: distribution appears uniform (no clustering)
      
      iv) Run Rayleigh test (circular concentration test):
         - Tests for directional/cyclic concentration
         - May reveal patterns that chi-square alone doesn't
         - Report statistic and p-value
      
      v) Calculate effect size:
         - Cramér's V = sqrt(χ² / (n * (k-1)))
         - Where n = total records, k = 16 bins
         - Measures strength of non-uniformity
      
      vi) Identify significant bins:
         - Which bins have significantly more records than expected?
         - Which bins have significantly fewer records than expected?
         - Calculate standardized residuals: (observed - expected) / sqrt(expected)

2. Generate synthetic null hypothesis catalogs:
   
   a) Create 1000 synthetic datasets:
      - For each synthetic catalog iteration:
        * Shuffle x_val, y_val, z_val values randomly
        * Keep a_val and v_val in original order (unchanged)
        * This randomizes the relationship between cycles and records
      
   b) For each synthetic catalog:
      - Run identical chi-square test on x_val, y_val, z_val
      - Store chi-square p-values for each variable
      - Store Cramér's V for each variable
   
   c) Generate p-value distribution:
      - Collect 1000 p-values for x_val synthetic tests
      - Collect 1000 p-values for y_val synthetic tests
      - Collect 1000 p-values for z_val synthetic tests

3. Compare real data to synthetic distribution:
   
   a) For each variable:
      - Calculate percentile rank of real p-value in synthetic distribution
      - If real p-value < 5th percentile: Pattern is NOT due to random chance
      - If real p-value > 95th percentile: Pattern may not be significant
      - If real p-value between 5th-95th percentile: Pattern exists but with some random component
   
   b) Generate comparison summary:
      - Which variable(s) show real clustering (p < 5th percentile of synthetic)?
      - Which variable(s) show no clustering (p > 95th percentile of synthetic)?
      - Rank variables by strength of non-uniformity

4. Output output/case_3a_results_blind.json containing:
```json
   {
     "sample_size": N,
     "binning_approach": "max(variable) / 16",
     "x_val": {
       "chi_square": {
         "statistic": X,
         "p_value": Y,
         "degrees_of_freedom": 15,
         "interpretation": "significant" or "not significant"
       },
       "rayleigh": {
         "statistic": Z,
         "p_value": W
       },
       "cramers_v": V,
       "significant_bins": {
         "excess": [list of bins with >expected],
         "deficit": [list of bins with <expected]
       },
       "bin_counts": [count_bin_1, count_bin_2, ..., count_bin_16],
       "expected_count_per_bin": N/16
     },
     "y_val": {...},
     "z_val": {...},
     "synthetic_null_hypothesis": {
       "synthetic_catalogs_generated": 1000,
       "shuffling_method": "x_val, y_val, z_val randomized; a_val, v_val preserved",
       "x_val_synthetic_p_values": [distribution of 1000 p-values],
       "y_val_synthetic_p_values": [distribution of 1000 p-values],
       "z_val_synthetic_p_values": [distribution of 1000 p-values],
       "percentile_rank_analysis": {
         "x_val_real_p_percentile": P,
         "y_val_real_p_percentile": P,
         "z_val_real_p_percentile": P
       }
     }
   }
```
5. Create src/visualization_case_3a_blind.py that generates:
   
   a) Three histograms (one per variable):
      - X-axis: bin labels 1-16 (sequential, not numeric values)
      - Y-axis: record count
      - Overlay horizontal line at "expected count per bin" (uniform baseline)
      - Color bars: green if significantly excess, red if significantly deficit, blue if not significant
      - Include chi-square p-value and Cramér's V on each plot
      - Titles: "x_val Distribution (16 bins)", "y_val Distribution (16 bins)", "z_val Distribution (16 bins)"
      - Save as output/case_3a_histogram_x_val_blind.png, etc.
   
   b) Three heatmaps (sequential view, one per variable):
      - X-axis: bin labels 1-16
      - Y-axis: year (or time period grouping if applicable from a_val)
      - Color intensity: record count in each (year, bin) cell
      - Shows whether non-uniformity is consistent across time or varies
      - Titles: "x_val Sequential Clustering", "y_val Sequential Clustering", "z_val Sequential Clustering"
      - Save as output/case_3a_heatmap_x_val_blind.png, etc.
   
   c) Null hypothesis comparison plot:
      - Three subplots (one per variable)
      - X-axis: synthetic p-value (0 to 1)
      - Y-axis: frequency (count of synthetic runs)
      - Histogram of 1000 synthetic p-values
      - Overlay vertical line at real data p-value
      - If real p-value is far left (< 5th percentile): pattern is real
      - If real p-value overlaps histogram: pattern could be random
      - Save as output/case_3a_null_hypothesis_comparison_blind.png
   
   d) Significance comparison plot:
      - X-axis: the three variables (x_val, y_val, z_val)
      - Y-axis: chi-square p-value (log scale)
      - Include horizontal lines at p=0.05 (significance threshold) and 5th/95th percentiles of synthetic
      - Shows which variables deviate significantly from uniformity
      - Save as output/case_3a_significance_comparison_blind.png

6. Create tests/test_case_3a_blind.py with assertions:
   - Assert sample size > 1000
   - For each variable:
     * Assert bin counts sum to total sample size
     * Assert chi-square test produces valid p-value (0-1)
     * Assert Cramér's V is between 0-1
     * Assert Rayleigh test produces valid p-value
   - Assert synthetic catalogs generated = 1000
   - Assert synthetic p-value distributions are populated
   - Verify percentile rank calculations are correct
   - All tests pass

7. Output output/case_3a_whitepaper_blind.md with:
   
   Standard header:
   ```
   # Case 3A: Clustering Patterns - Full Population (Blind Study - Approach Two)
   
   **Document Information**
   - Version: 1.0
   - Date: [current date]
   - Data: Anonymized full population (a_val, v_val, x_val, y_val, z_val)
   - Project: Blind Study (Approach Two) - ISOLATED ANALYSIS
   - Purpose: Detect clustering patterns in variables x_val, y_val, z_val
   ```
   
   Methodology section:
   - Explain 16-bin approach: "Bin size = [max value] / 16 for each variable"
   - Explain chi-square uniformity test
   - Explain Rayleigh circular concentration test
   - Explain Cramér's V effect size
   - Explain null hypothesis synthetic catalog generation
   - Explain how synthetic catalogs are generated (values randomized, structure preserved)
   - Explain percentile rank interpretation (5th/95th percentile thresholds)
   
   Results section (ONE SUBSECTION PER VARIABLE):
   
   **x_val Clustering Analysis:**
   - Chi-square: χ² = X, p-value = Y (significant/not significant)
   - Rayleigh: statistic = Z, p-value = W
   - Cramér's V = V (effect size interpretation: small/moderate/large)
   - Bins with significant excess: [list bin numbers and percentage excess]
   - Bins with significant deficit: [list bin numbers and percentage deficit]
   - Null hypothesis result: Real p-value ranks at Pth percentile of 1000 synthetic values
     * If P < 5: Pattern is NOT due to random chance (robust finding)
     * If P > 95: Pattern may be due to random variation
     * If 5 < P < 95: Pattern exists with some random component
   
   **y_val Clustering Analysis:**
   [Same structure as x_val]
   
   **z_val Clustering Analysis:**
   [Same structure as x_val]
   
   Comparative Analysis section:
   - Summary of which variables show significant clustering
   - Ranking by strength: which variable has strongest signal?
   - Ranking by robustness: which variable is least likely due to chance?
   - Which variable(s) show no clustering?
   - What patterns emerge when comparing x_val vs y_val vs z_val?
   - Are the clustering patterns similar or distinct across variables?
   
   Null Hypothesis Validation section:
   - Summary of synthetic catalog approach
   - Results: which real p-values fall in tails of synthetic distribution?
   - Interpretation: Do results support that clustering is real (not random)?
   - What is the confidence level that observed patterns are genuine?
   
   Limitations section:
   - Note that we have not identified what variables represent
   - Note that we cannot interpret the physical meaning of clustering
   - Note that we are performing pure statistical pattern detection
   - Note that future cases will test for specific types of patterns within this clustering
