FIREWALL REMINDER: This is a blind study analysis. You have no knowledge 
of what x_val, y_val, z_val represent or what patterns are expected. 
Analyze objectively and report what the data shows.

I have anonymized data in data/record_vals.csv with columns:
a_val, v_val, x_val, y_val, z_val (all numeric)

From Case 0, we understand the basic distributions. Now test whether 
x_val, y_val, and z_val show uniform or non-uniform distributions across 
their ranges. This tests whether events are randomly distributed or show 
clustering patterns.

1. Create src/case_1_blind_analysis.py that:
   
   For EACH variable (x_val, y_val, z_val):
   a) Create 16 equal bins across the range [min, max]
      - Bin size = (max - min) / 16
   
   b) Count observations in each bin
   
   c) Run chi-square goodness-of-fit test:
      - Null hypothesis: observations are uniformly distributed across bins
      - Expected count per bin = total_observations / 16
      - Calculate χ² statistic and p-value
      - If p < 0.05: distribution is NOT uniform (clustering exists)
      - If p > 0.05: distribution appears uniform (no clustering)
   
   d) Run Rayleigh test (if applicable for circular data):
      - Tests for directional concentration
      - Provides alternative perspective on clustering
   
   e) Calculate effect size:
      - Cramér's V = sqrt(χ² / (n * (k-1)))
      - Where n = total observations, k = number of bins
      - Measures strength of non-uniformity
   
   f) Store results with variable context

2. Output output/case_1_results_blind.json containing:
   {
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
       "effect_size_cramers_v": V,
       "sample_size": N,
       "bin_counts": [count_bin_1, count_bin_2, ..., count_bin_16],
       "expected_count_per_bin": N/16
     },
     "y_val": {...},
     "z_val": {...}
   }

3. Create src/visualization_case_1_blind.py that:
   - Generates three histograms (one per variable):
     * X-axis: 16 bins (labeled 1-16 sequentially)
     * Y-axis: observation count
     * Overlay horizontal line at "expected count per bin" (uniform baseline)
     * Title includes variable name and chi-square p-value
     * Save as output/case_1_histogram_x_val_blind.png, etc.
   
   - Generates comparison plot:
     * X-axis: the three variables (x_val, y_val, z_val)
     * Y-axis: chi-square p-value (with 0.05 significance line)
     * Shows which variables deviate from uniform distribution
     * Save as output/case_1_significance_comparison_blind.png

4. Create tests/test_case_1_blind.py with assertions:
   - For each variable:
     * Assert sample size > 0
     * Calculate whether chi-square p-value is <0.05 (significant)
     * Assert effect size (Cramér's V) is calculated correctly
   - Compare results across variables (which show clustering? which don't?)
   - All tests should pass

5. Output output/case_1_whitepaper_blind.md with:
   
   Standard header:
   ```
   # Case 1: Distribution Uniformity Testing (Blind Study - Approach Two)
   
   **Document Information**
   - Version: 1.0
   - Date: [current date]
   - Data: Anonymized columns (a_val, v_val, x_val, y_val, z_val)
   - Project: Blind Study (Approach Two) - ISOLATED ANALYSIS
   - Purpose: Test whether variables show uniform or clustering patterns
   ```
   
   Population Summary (from Case 0):
   - Restate basic statistics for x_val, y_val, z_val
   
   Methodology section:
   - Explain chi-square test for uniformity
   - Explain Rayleigh test (if used)
   - Define effect size (Cramér's V)
   - Explain 16-bin approach
   
   Results section (ONE SUBSECTION PER VARIABLE):
   
   **x_val Distribution:**
   - Chi-square: χ² = X, p = Y (significant/not significant)
   - Rayleigh: Z = A, p = B
   - Cramér's V = C (effect size)
   - Interpretation: x_val shows [uniform/non-uniform] distribution
   - Observations cluster in bins: [list bins with >expected count]
   - Observations sparse in bins: [list bins with <expected count]
   
   **y_val Distribution:**
   [Same structure]
   
   **z_val Distribution:**
   [Same structure]
   
   Comparative Analysis section:
   - Which variable(s) show significant deviation from uniformity?
   - Which variable(s) appear uniformly distributed?
   - Rank variables by effect size (strongest signal to weakest)
   - Note: Do not interpret what this means yet. Just report the finding.
   
   Limitations section:
   - Note that we have not identified what variables represent
   - Note that we cannot interpret meaning of clustering patterns
   - Note that next cases will test for specific types of patterns
   