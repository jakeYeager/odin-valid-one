I have a CSV file data/record_vals.csv with anonymized numeric columns:
a_val, v_val, x_val, y_val, z_val

This is exploratory analysis to understand population characteristics before 
conducting statistical tests. Generate comprehensive visualizations and 
population report.

1. Create src/case_0_population_analysis.py that:
   
   a) Load data/record_vals.csv
   
   b) For each column (a_val, v_val, x_val, y_val, z_val), calculate:
      - Total count of records
      - Min value
      - Max value
      - Mean
      - Median
      - Standard deviation
      - Any missing values
   
   c) Identify unique values in a_val (will be y-axis groups for heatmaps)

2. Create src/visualization_case_0.py that generates:

   **HISTOGRAMS (3 total)**
   
   1. Histogram for x_val:
      - Bin size: [max x_val] / 16
      - X-axis: sequential bin labels "1", "2", "3", ... "16"
      - Y-axis: event count
      - Title: "Distribution of x_val (16 equal bins)"
      - Save as: output/case_0_histogram_x_val.png
   
   2. Histogram for y_val:
      - Bin size: [max y_val] / 16
      - X-axis: sequential bin labels "1", "2", "3", ... "16"
      - Y-axis: event count
      - Title: "Distribution of y_val (16 equal bins)"
      - Save as: output/case_0_histogram_y_val.png
   
   3. Histogram for z_val:
      - Bin size: [max z_val] / 16
      - X-axis: sequential bin labels "1", "2", "3", ... "16"
      - Y-axis: event count
      - Title: "Distribution of z_val (16 equal bins)"
      - Save as: output/case_0_histogram_z_val.png

   **HEATMAPS (6 total)**
   
   4. Heatmap: x_val (x-axis) vs a_val (y-axis):
      - X-axis: 16 equal bins of x_val, labeled "1" through "16"
      - Y-axis: unique a_val values, labeled as-is
      - Color intensity: count of records in each (x_val_bin, a_val) cell
      - Colormap: default (viridis or similar)
      - Title: "x_val bins vs a_val groups (all records)"
      - Save as: output/case_0_heatmap_x_vs_a_all.png
   
   5. Heatmap: x_val (x-axis) vs a_val (y-axis), WHERE v_val >= 7.0:
      - X-axis: 16 equal bins of x_val, labeled "1" through "16"
      - Y-axis: unique a_val values, labeled as-is
      - Color intensity: count of records in each cell (v_val >= 7.0 only)
      - Colormap: blues
      - Title: "x_val bins vs a_val groups (v_val >= 7.0)"
      - Save as: output/case_0_heatmap_x_vs_a_v7.png
   
   6. Heatmap: x_val (x-axis) vs y_val (y-axis):
      - X-axis: 16 equal bins of x_val, labeled "1" through "16"
      - Y-axis: 16 equal bins of y_val, labeled "1" through "16"
      - Color intensity: count of records in each (x_val_bin, y_val_bin) cell
      - Colormap: default (viridis or similar)
      - Title: "x_val bins (16) vs y_val bins (16) (all records)"
      - Save as: output/case_0_heatmap_x_vs_y_all.png
   
   7. Heatmap: x_val (x-axis) vs y_val (y-axis), WHERE v_val >= 7.0:
      - X-axis: 16 equal bins of x_val, labeled "1" through "16"
      - Y-axis: 16 equal bins of y_val, labeled "1" through "16"
      - Color intensity: count of records in each cell (v_val >= 7.0 only)
      - Colormap: blues
      - Title: "x_val bins (16) vs y_val bins (16) (v_val >= 7.0)"
      - Save as: output/case_0_heatmap_x_vs_y_v7.png
   
   8. Heatmap: y_val (x-axis) vs z_val (y-axis):
      - X-axis: 16 equal bins of y_val, labeled "1" through "16"
      - Y-axis: 16 equal bins of z_val, labeled "1" through "16"
      - Color intensity: count of records in each (y_val_bin, z_val_bin) cell
      - Colormap: default (viridis or similar)
      - Title: "y_val bins (16) vs z_val bins (16) (all records)"
      - Save as: output/case_0_heatmap_y_vs_z_all.png
   
   9. Heatmap: y_val (x-axis) vs z_val (y-axis), WHERE v_val >= 7.0:
      - X-axis: 16 equal bins of y_val, labeled "1" through "16"
      - Y-axis: 16 equal bins of z_val, labeled "1" through "16"
      - Color intensity: count of records in each cell (v_val >= 7.0 only)
      - Colormap: blues
      - Title: "y_val bins (16) vs z_val bins (16) (v_val >= 7.0)"
      - Save as: output/case_0_heatmap_y_vs_z_v7.png

3. Create output/case_0_results.json containing:
   - For each column (a_val, v_val, x_val, y_val, z_val):
     {
       "column_name": "x_val",
       "total_count": N,
       "min": value,
       "max": value,
       "mean": value,
       "median": value,
       "std_dev": value,
       "missing_count": 0
     }
   - List of unique a_val values

4. Create output/case_0_whitepaper.md that includes:

   Population Summary section:
   - Total record count
   - For each column: min, max, mean, median, std dev
   - Note about missing values (if any)
   - List of unique a_val group values and their counts
   
   Data Quality section:
   - Any observations about data distribution
   - Completeness assessment
   - Any anomalies or interesting patterns
   
   Visualization sections:
   - Histogram section: Describe x_val, y_val, z_val distributions
   - Heatmap section: Describe relationships:
     * x_val vs a_val (all and v_val >= 7.0 filtered)
     * x_val vs y_val (all and v_val >= 7.0 filtered)
     * y_val vs z_val (all and v_val >= 7.0 filtered)
   - Note any clustering, patterns, or deviations from uniform distribution
   - Note impact of v_val >= 7.0 filter (does it change patterns?)

5. No tests required for Case 0 (exploratory phase)