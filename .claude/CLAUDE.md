# Blind Study Analysis - APPROACH TWO ONLY

## Project Context
This is a statistical analysis of anonymized data. This data is located in two files: `data/record_vals.csv` with columns: a_val, v_val, x_val, y_val, z_val (numeric values only). The other data file `data/timestamp_vals.csv` as columns v_val and timestamp.

## Data Description
- Total records: [to be determined]
- Variables: a_val, v_val, x_val, y_val, z_val (all numeric)
- No context provided about what variables represent
- Purpose: Analyze statistical relationships and distributions

## Analysis Framework
Cases 0-4 test for patterns in the data:
- Case 0: Population description for x_val, y_val and z_val
- Case 1: Statistical uniform or non-uniform distribution testing for x_val, y_val and z_val
- Case 2-4: Statistical significance testing


## Standards & Conventions

### File Organization

```
odin-valid-one/
├── .claude/CLAUDE.md                (this file)
├── README.md                        (blind study documentation)
├── data/
│   ├── timestamps.csv
│   └── record_vals.csv              (only anonymized data)
├── src/
│   ├── case_0_population_analysis.py
│   ├── case_1_blind_analysis.py
│   ├── visualization_case_0_blind.py
│   └── utils_blind.py
├── tests/
│   ├── test_case_0_blind.py
│   └── test_case_1_blind.py
└── output/
    ├── case_0_results.json
    ├── case_0_whitepaper.md
    ├── case_0_histogram_*.png
    ├── case_0_heatmap_*.png
    └── [future case outputs]
```

### Metadata Standards

Every whitepaper output should include:

**Header:**
```markdown
# Case X: [Objective Description Based on Data Findings]

**Document Information**
- Version: 1.0
- Date: [current date]
- Approach: Blind Study (Approach Two)
- Data: Anonymized
- Purpose: Independent statistical validation
```

**Footer:**
```markdown
---

**Generation Details**
- Version: 1.0
- Date: [current date]
- Planning prepared with: Claude.ai Web Interface (Haiku 4.5)
- Generated with: Claude Code 2.1.31 (Claude Model Opus 4.5)
- Project: Approach Two Blind Study - ISOLATED ANALYSIS
- Isolation Status: Complete separation from main project
```

### Statistical Standards

- **Significance threshold:** p < 0.05
- **Effect size metric:** Cramér's V (dimensionless, 0-1 scale)
- **Null hypothesis approach:** Always compare to randomized baseline
- **Test suite:** Comprehensive assertions validating findings
- **Transparency:** All p-values, test statistics, and parameters reported

### Output Naming

All files should include `_blind` or note isolation status:

```
case_0_results.json              ← Clearly labeled
case_0_histogram_a_val.png       ← Variable analyzed
case_0_whitepaper.md             ← Standard format
case_1_analysis_blind.py         ← Code identifies as blind analysis
test_case_0_blind.py             ← Test file
```
---

## What NOT to Do

### Do NOT Assume Anything

- Do not assume variables represent anything (time cycles, volumns, etc.)
- Do not assume patterns SHOULD exist
- Do not assume any specific interpretation
- Do not expect findings to match anything else

### Do NOT Look At

- Any interpretive documents
- Any hypothesis statements
- Any external context

### Do NOT Make

- Connections to real-world phenomena
- Interpretations based on variable names
- Predictions about outcomes
- Assumptions about expected results
- Inferences from the main project

---

## What TO Do

### Do Analyze Objectively

1. Load the data as numbers
2. Apply statistical tests
3. Report results numerically
4. Identify significant patterns
5. Measure effect sizes
6. Compare to randomized baseline

### Do Document Everything

- Record every statistical test performed
- Report all p-values and test statistics
- Note sample sizes and degrees of freedom
- Document any data cleaning or filtering
- Explain methodology in whitepaper

### Do Compare Results

After completing Case 0 and subsequent cases:
- Note which variables show patterns
- Note which variables show no pattern
- Measure effect sizes objectively
- Report confidence intervals
- Quantify uncertainty

### Do Maintain Firewall

- Keep this directory isolated
- Don't cross-reference main project
- Don't read main project findings during analysis
- Don't let external knowledge influence code
- Document isolation in all outputs