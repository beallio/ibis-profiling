# /// script
# dependencies = [
#   "ibis-framework[duckdb]",
#   "polars",
#   "pyarrow",
#   "numpy",
#   "psutil",
# ]
# ///
from pathlib import Path
import polars as pl
import random
import os
import shutil
import psutil
import gc


def get_mem_mb():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)


def generate_single_file_20M(total_rows: int, output_file: str, chunk_size: int = 2_000_000):
    # 1. Setup a temporary directory for our chunks
    temp_dir = Path(output_file).parent / ".temp_parquet_chunks"
    os.makedirs(temp_dir, exist_ok=True)

    print(f"[{get_mem_mb():.2f} MB] Starting chunked generation...")

    # 2. Generate and write chunks to the temp folder
    for start_idx in range(0, total_rows, chunk_size):
        current_chunk_size = min(chunk_size, total_rows - start_idx)
        file_path = f"{temp_dir}/part_{start_idx}.parquet"

        pl.select(
            id=pl.int_range(start_idx, start_idx + current_chunk_size, dtype=pl.Int64),
            date_col=pl.int_range(
                1600000000 + start_idx, 1600000000 + start_idx + current_chunk_size, dtype=pl.Int64
            ),
            const_int=pl.repeat(42, n=current_chunk_size, dtype=pl.Int32),
            empty_strings=pl.repeat("", n=current_chunk_size, dtype=pl.String),
            int_col=pl.int_range(0, 1000, dtype=pl.Int32).sample(
                current_chunk_size, with_replacement=True
            ),
            cat_high=pl.int_range(0, 10000, dtype=pl.Int32)
            .sample(current_chunk_size, with_replacement=True)
            .cast(pl.String),
            bool_col=pl.Series([True, False]).sample(current_chunk_size, with_replacement=True),
            cat_low=pl.Series(["A", "B", "C"]).sample(current_chunk_size, with_replacement=True),
            random_str=pl.Series(["foo", "bar", "baz", "qux"]).sample(
                current_chunk_size, with_replacement=True
            ),
            float_col=pl.Series(
                [random.random() for _ in range(current_chunk_size)], dtype=pl.Float32
            ),
            extra_1=pl.Series(
                [random.uniform(0, 100) for _ in range(current_chunk_size)], dtype=pl.Float32
            ),
            extra_2=pl.Series(
                [random.uniform(0, 100) for _ in range(current_chunk_size)], dtype=pl.Float32
            ),
            extra_3=pl.Series(
                [random.uniform(0, 100) for _ in range(current_chunk_size)], dtype=pl.Float32
            ),
        ).write_parquet(file_path)
        gc.collect()  # Force garbage collection to free memory after each chunk

        print(
            f"[{get_mem_mb():.2f} MB] Wrote temp chunk {start_idx} to {start_idx + current_chunk_size}"
        )

    # 3. Stream all the temporary chunks into one final file
    print(f"\n[{get_mem_mb():.2f} MB] Streaming chunks into single file '{output_file}'...")
    # sink_parquet is a lazy operation that streams data to disk with low memory
    pl.scan_parquet(f"{temp_dir}/*.parquet").sink_parquet(output_file)

    # 4. Clean up the temporary folder
    print(f"[{get_mem_mb():.2f} MB] Cleaning up temporary files...")
    shutil.rmtree(temp_dir)

    print(f"[{get_mem_mb():.2f} MB] Done. Your single file is ready.")


if __name__ == "__main__":
    total_rows = 20_000_000
    output_filepath = "/tmp/ibis-profiling/data_20M_13cols.parquet"
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    generate_single_file_20M(total_rows=total_rows, output_file=output_filepath)
