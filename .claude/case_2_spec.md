FIREWALL REMINDER: This is a blind study. You have no knowledge of what
the timestamp data represents or what patterns are expected. Analyze 
objectively for temporal clustering without assumptions about distributions.

I have anonymized timestamp data in data/timestamp_vals.csv with:
- Column `v_val`: numeric values (context unknown)
- Column `timestamp`: ISO8601 format timestamps (e.g., "2020-01-15T12:34:56Z")

From this, you need to:
1. Calculate inter-event time intervals (time elapsed between consecutive events)
2. Test whether these intervals show clustering (non-random temporal spacing) 
   or appear randomly distributed

This complements Case 1 by analyzing the TIMING of events rather than their distribution properties.

1. Create src/case_2_blind_analysis.py that:
   
   a) Load and preprocess data:
      - Load data/timestamp_vals.csv
      - Parse timestamp column as datetime objects (handle ISO8601 format)
      - Sort records by timestamp in chronological order
      - Calculate inter-event intervals: Δt[i] = timestamp[i+1] - timestamp[i]
      - Convert intervals to days (numeric, floating point)
      - Remove any invalid intervals (must be > 0)
      - Verify preprocessing: log number of valid intervals
   
   b) Calculate basic interval statistics:
      - Sample size: N = number of intervals
      - Min interval: minimum value
      - Max interval: maximum value
      - Mean interval: average
      - Median interval: 50th percentile
      - Std dev: standard deviation
      - Q1, Q3: first and third quartiles
      - IQR: interquartile range
   
   c) Test for temporal clustering using multiple approaches:
      
      APPROACH 1: Chi-square uniformity test on log-binned intervals
      - Create 16 equal bins in log10(interval_days) space
        * min_log = log10(min_interval)
        * max_log = log10(max_interval)
        * bin_size = (max_log - min_log) / 16
      - Count intervals in each bin
      - Run chi-square test: H₀ = uniform distribution in log space
      - Calculate χ² statistic, p-value, Cramér's V
      - Interpretation: Does clustering exist in interval lengths?
      
      APPROACH 2: KS test against exponential distribution
      - Fit exponential distribution to intervals (Poisson process baseline)
        * λ = 1 / mean_interval
      - Calculate Kolmogorov-Smirnov statistic and p-value
      - If p > 0.05: intervals consistent with random Poisson process
      - If p < 0.05: intervals deviate from randomness (clustering detected)
      
      APPROACH 3: Coefficient of variation analysis
      - CV = std_dev / mean
      - For random (exponential) process: CV ≈ 1.0
      - CV > 1.5: indicates clustering (some very short, some very long intervals)
      - CV < 0.7: indicates regularity (intervals more uniform than random)
   
   d) Calculate additional clustering indicators:
      - Ratio of max interval to min interval (spread)
      - Count of intervals < median (clustering indicator)
      - Count of intervals > 3× mean (extreme long gaps)
      - Proportion of very short intervals

2. Output output/case_2_results_blind.json containing:
   {
     "data_processing": {
       "total_records_loaded": N,
       "valid_intervals_calculated": M,
       "date_range_start": "YYYY-MM-DD",
       "date_range_end": "YYYY-MM-DD",
       "timestamp_parsing_status": "success"
     },
     "interval_statistics": {
       "sample_size": N,
       "min_days": X,
       "max_days": Y,
       "mean_days": Z,
       "median_days": M,
       "std_dev": S,
       "q1_days": Q1,
       "q3_days": Q3,
       "iqr_days": IQR
     },
     "uniformity_test": {
       "chi_square": {
         "statistic": X,
         "p_value": Y,
         "degrees_of_freedom": 15,
         "interpretation": "significant" or "not significant"
       },
       "cramers_v": V,
       "bin_counts": [counts for 16 log-bins]
     },
     "exponential_baseline_test": {
       "ks_statistic": X,
       "ks_p_value": Y,
       "lambda_parameter": L,
       "interpretation": "consistent with random" or "deviates from random"
     },
     "clustering_analysis": {
       "coefficient_of_variation": CV,
       "cv_interpretation": "clustering" or "random" or "regular",
       "max_min_ratio": MAX/MIN,
       "clustering_indicators": {
         "intervals_less_than_median": count,
         "intervals_greater_than_3x_mean": count,
         "proportion_short_intervals": fraction
       }
     }
   }

3. Create src/visualization_case_2_blind.py that generates:
   
   a) Histogram of raw intervals:
      - X-axis: interval_days (linear scale)
      - Y-axis: count
      - Title: "Distribution of Inter-Event Intervals (Linear)"
      - Show median and mean lines
      - Save as output/case_2_histogram_linear_blind.png
   
   b) Histogram of log-transformed intervals:
      - X-axis: log10(interval_days)
      - Y-axis: count (16 bins in log space)
      - Overlay uniform distribution baseline
      - Include chi-square p-value on plot
      - Save as output/case_2_histogram_log_blind.png
   
   c) Q-Q plot: observed vs exponential distribution:
      - Compares observed intervals to exponential baseline
      - If points follow diagonal = consistent with exponential (random)
      - If points deviate = suggests clustering
      - Save as output/case_2_qq_plot_exponential_blind.png
   
   d) Sorted interval plot (cumulative view):
      - X-axis: interval rank (1st shortest to Nth longest)
      - Y-axis: interval duration in days (log scale)
      - Shows tail behavior and clustering patterns
      - Save as output/case_2_sorted_intervals_blind.png

4. Create tests/test_case_2_blind.py with assertions:
   - Assert valid_intervals > 100
   - Assert min_interval > 0
   - Assert max_interval > min_interval
   - Assert mean and median are calculated correctly
   - Assert all statistics are positive numbers
   - Assert chi-square test produces valid p-value (0-1)
   - Assert KS test produces valid p-value (0-1)
   - Assert coefficient of variation is calculated correctly
   - All tests pass

5. Output output/case_2_whitepaper_blind.md with:
   
```
   # Case 2: Inter-Event Interval Analysis (Blind Study - Approach Two)
   
   **Document Information**
   - Version: 1.0
   - Date: [current date]
   - Data: Anonymized timestamp intervals (calculated from timestamps)
   - Project: Blind Study (Approach Two) - ISOLATED ANALYSIS
   - Purpose: Detect clustering in temporal spacing of events
   ```
   
   Data Processing section:
   - Description of preprocessing: parsing ISO8601 timestamps, calculating intervals
   - Total records loaded: N
   - Valid intervals calculated: M
   - Date range of data: START to END
   - Any data quality issues or notes
   
   Sample Description section:
   - Number of intervals analyzed
   - Time span of dataset
   - Minimum interval: X days
   - Maximum interval: Y days
   - Mean interval: Z days
   - Median interval: M days
   - Standard deviation: S days
   - Range (max/min ratio): R
   
   Methodology section:
   - Explain how intervals were calculated from timestamps
   - Explain chi-square uniformity test (what it tests, what p-value means)
   - Explain exponential distribution baseline (random Poisson process)
   - Explain KS test (measures deviation from baseline)
   - Explain coefficient of variation (clustering metric)
   - Explain why 16 bins chosen
   
   Results section:
   
   **Uniformity Test Results:**
   - χ² = X, p-value = Y (significant/not significant)
   - Cramér's V = C (effect size)
   - Interpretation: Intervals [do/do not] show non-random clustering in length
   - Bins with excess events: [list which log-bins have > expected count]
   - Bins with deficit events: [list which log-bins have < expected count]
   
   **Exponential Baseline Test:**
   - KS statistic = X
   - p-value = Y
   - Interpretation: Intervals [are/are not] consistent with random Poisson process
   - If p < 0.05: Intervals significantly deviate from exponential (clustering detected)
   - If p > 0.05: Intervals consistent with random process (no clustering)
   
   **Coefficient of Variation:**
   - CV = X
   - Interpretation: [Indicates clustering / Indicates regularity / Random process]
   - Quartile analysis: Q1 = A, Q3 = B, IQR = C
   
   **Clustering Indicators:**
   - Proportion of intervals shorter than median: X%
   - Proportion of intervals longer than 3× mean: Y%
   - Max-to-min interval ratio: R
   
   Comparative Summary section:
   - Do the statistics indicate temporal clustering or randomness?
   - Which test (chi-square, KS, CV) provides strongest evidence?
   - Any patterns observable in the interval distribution?
   
   Limitations section:
   - Note that we have not identified what the events represent
   - Note that we cannot interpret the physical meaning of clustering
   - Note that next cases will provide additional context
   