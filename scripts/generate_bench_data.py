import polars as pl
import numpy as np
from faker import Faker
import argparse
import os


def generate_bench_data_chunk(n_rows, start_id, rng, fake):
    # 1. id: Unique integer
    ids = np.arange(start_id, start_id + n_rows)

    # 2. const_str
    const_str = np.full(n_rows, "fixed_value")

    # 3. mostly_null
    mostly_null = rng.choice([np.nan, 1.0], size=n_rows, p=[0.6, 0.4])

    # 4. mostly_zero
    mostly_zero = rng.choice([0.0, 1.0], size=n_rows, p=[0.95, 0.05])

    # 5. high_card
    pool_size = 10000
    card_pool = [f"user_{i}" for i in range(pool_size)]
    high_card = rng.choice(card_pool, size=n_rows)

    # 6. skewed
    skewed = rng.exponential(scale=2.0, size=n_rows)

    # 7. corr_base
    corr_base = rng.normal(0, 1, size=n_rows)

    # 8. corr_high
    corr_high = corr_base + rng.normal(0, 0.01, size=n_rows)

    # 9. num_uniform
    num_uniform = rng.uniform(0, 100, size=n_rows)

    # 10. num_normal
    num_normal = rng.normal(50, 10, size=n_rows)

    # 11. cat_low
    cat_low = rng.choice(["A", "B", "C", "D", "E"], size=n_rows)

    # 12. cat_med
    cat_med_pool = [f"cat_{i}" for i in range(50)]
    cat_med = rng.choice(cat_med_pool, size=n_rows)

    # 13. bool_true
    bool_true = np.full(n_rows, True)

    # 14. bool_mixed
    bool_mixed = rng.choice([True, False], size=n_rows)

    # 15. text_short
    text_short_pool = [fake.word() for _ in range(1000)]
    text_short = rng.choice(text_short_pool, size=n_rows)

    # 16. text_long
    text_long_pool = [fake.paragraph(nb_sentences=3) for _ in range(500)]
    text_long = rng.choice(text_long_pool, size=n_rows)

    # 17. int_pos
    int_pos = rng.integers(1, 1000000, size=n_rows)

    # 18. int_neg
    int_neg = rng.integers(-1000000, -1, size=n_rows)

    # 19. float_small
    float_small = rng.random(size=n_rows)

    # 20. float_large
    float_large = rng.uniform(1e6, 1e9, size=n_rows)

    data = {
        "id": ids,
        "const_str": const_str,
        "mostly_null": mostly_null,
        "mostly_zero": mostly_zero,
        "high_card": high_card,
        "skewed": skewed,
        "corr_base": corr_base,
        "corr_high": corr_high,
        "num_uniform": num_uniform,
        "num_normal": num_normal,
        "cat_low": cat_low,
        "cat_med": cat_med,
        "bool_true": bool_true,
        "bool_mixed": bool_mixed,
        "text_short": text_short,
        "text_long": text_long,
        "int_pos": int_pos,
        "int_neg": int_neg,
        "float_small": float_small,
        "float_large": float_large,
    }

    return pl.DataFrame(data)


def main():
    parser = argparse.ArgumentParser(description="Memory-efficient data generator.")
    parser.add_argument("--rows", type=int, default=100000)
    parser.add_argument("--output", type=str, default="/tmp/ibis-profiling/bench_data.parquet")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    print(f"Generating {args.rows:,} rows x 20 columns in chunks...")

    rng = np.random.default_rng(42)
    fake = Faker()
    Faker.seed(42)

    chunk_size = 1_000_000
    n_chunks = (args.rows + chunk_size - 1) // chunk_size

    for i in range(n_chunks):
        rows_to_gen = min(chunk_size, args.rows - i * chunk_size)
        start_id = i * chunk_size
        print(f"  Chunk {i + 1}/{n_chunks} ({rows_to_gen:,} rows)...")
        df = generate_bench_data_chunk(rows_to_gen, start_id, rng, fake)

        if i == 0:
            df.write_parquet(args.output)
        else:
            # Append is not directly supported in sink_parquet easily without scanning
            # For this benchmark, we'll collect all and write if small,
            # or use a more complex streaming approach if needed.
            # Actually, let's use a list and concat if it's not too huge,
            # or just write chunks and use ibis to read them all.
            # Better: Write to temporary files and use duckdb to combine them.
            chunk_path = f"{args.output}.chunk{i}"
            df.write_parquet(chunk_path)

    if n_chunks > 1:
        print("Combining chunks...")
        import ibis

        con = ibis.duckdb.connect()
        # Combine all chunks
        # First chunk was written to args.output

        # We need to move it to .chunk0
        os.rename(args.output, f"{args.output}.chunk0")

        table = con.read_parquet(f"{args.output}.chunk*")
        table.to_parquet(args.output)

        # Cleanup
        import glob

        for f in glob.glob(f"{args.output}.chunk*"):
            os.remove(f)

    print(f"Saved to {args.output}")


if __name__ == "__main__":
    main()
