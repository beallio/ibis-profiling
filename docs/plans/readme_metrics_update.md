# Problem Definition
The README.md needs a comprehensive update to document how each metric shown in the generated templates is derived and calculated. The current documentation only briefly covers a few core statistics, advanced statistics, and alerts. A thorough review of the templates (`default.html`, `ydata-like.html`) and calculation logic (`metrics.py`, `report.py`, `inspector.py`) reveals many undocumented metrics like dataset memory sizes, coefficient of variation, quantiles, missingness metrics, etc.

# Architecture Overview
We will update the `README.md` file, specifically expanding the `## 📏 Metrics & Calculation Reference` section.

# Plan Details
We will replace the existing `## 📏 Metrics & Calculation Reference` section with a highly detailed one that maps exactly to what users see in the templates.

The new section will include:
1. **Dataset Statistics (Overview)**
   - Number of variables, observations, missing cells, duplicate rows, memory size.
2. **Variable Level Statistics (Numeric & Categorical)**
   - Overview metrics: Distinct, Missing, Infinite, Mean, Min, Max, Zeros, Negative.
   - Quantile Statistics: Percentiles, Range, IQR.
   - Descriptive Statistics: Variance, Std Dev, CV, Kurtosis, MAD, Skewness, Sum, Monotonicity.
   - Text Metrics: Min, Mean, Max lengths.
3. **Advanced Visualizations & Matrices**
   - Interactions, Nullity Matrices, Correlations.
4. **Alert Engine Logic** (preserving existing info).

This documentation update will fulfill the user's request to be thorough.

# Verification Strategy
- Verify that `README.md` contains the new text.
- No tests are required as this is purely a documentation update.
