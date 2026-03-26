"""Constants for ibis-profiling."""

# Metrics that are only applicable to numeric columns and should be removed
# if a column is reclassified to Categorical.
NUMERIC_ONLY_METRICS = {
    "mean",
    "std",
    "variance",
    "skewness",
    "kurtosis",
    "mad",
    "sum",
    "range",
    "iqr",
    "50%",
    "5%",
    "25%",
    "75%",
    "95%",
    "cv",
    "p_zeros",
    "p_infinite",
    "p_negative",
    "n_zeros",
    "n_infinite",
    "n_negative",
}
