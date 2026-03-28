import ibis
import os
from ibis_profiling import Profiler


def generate_reports(path="/tmp/ibis-profiling/verify_varied_5M.parquet"):
    print(f"Loading 5M data from {path}...")
    con = ibis.duckdb.connect()
    table = con.read_parquet(path)

    # Use standard threshold (1M) - cat_high and num_high_card should skip
    profiler = Profiler(
        table,
        title="Varied Data 5M Report",
        correlations=False,
        monotonicity=False,
        compute_duplicates=False,
    )

    print("Generating HTML report...")
    report = profiler.run()

    output_dir = "/tmp/ibis-profiling/varied_test"
    os.makedirs(output_dir, exist_ok=True)

    report.to_file(f"{output_dir}/varied_matrices.html")
    report.to_file(f"{output_dir}/varied_matrices.json")

    print(f"Reports generated in {output_dir}")


if __name__ == "__main__":
    generate_reports()
