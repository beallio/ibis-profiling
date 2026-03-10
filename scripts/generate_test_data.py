import polars as pl
from faker import Faker
import argparse
import os
import random
from datetime import datetime, timedelta


def generate_loan_data(fake, n_rows):
    data = []
    for i in range(n_rows):
        data.append(
            {
                "loan_id": i,
                "customer_id": fake.random_int(min=100000, max=999999),
                "loan_amount": float(fake.random_int(min=1000, max=50000)),
                "interest_rate": random.uniform(0.01, 0.15),
                "term_months": random.choice([12, 24, 36, 48, 60]),
                "application_date": fake.date_time_between(start_date="-2y", end_date="now"),
                "status": random.choice(["approved", "pending", "rejected", "funded"]),
                "is_secured": fake.boolean(),
                "credit_score": fake.random_int(min=300, max=850),
            }
        )
    return pl.DataFrame(data)


def generate_bank_data(fake, n_rows):
    data = []
    start_date = datetime(2023, 1, 1)
    for i in range(n_rows):
        data.append(
            {
                "transaction_id": fake.uuid4(),
                "account_id": fake.random_int(min=1000, max=5000),
                "amount": float(fake.random_int(min=-5000, max=5000)),
                "timestamp": start_date + timedelta(minutes=i * random.randint(1, 60)),
                "category": random.choice(
                    ["groceries", "rent", "salary", "entertainment", "travel"]
                ),
                "merchant": fake.company(),
                "city": fake.city(),
            }
        )
    return pl.DataFrame(data)


def generate_population_data(fake, n_rows):
    data = []
    for i in range(n_rows):
        data.append(
            {
                "person_id": i,
                "name": fake.name(),
                "age": fake.random_int(min=0, max=100),
                "gender": random.choice(["M", "F", "Other", "Unknown"]),
                "income": float(fake.random_int(min=0, max=200000))
                if random.random() > 0.1
                else None,
                "education": random.choice(["high_school", "bachelors", "masters", "phd", None]),
                "country": fake.country(),
                "is_active": fake.boolean(),
            }
        )
    return pl.DataFrame(data)


def generate_legacy_loan_data(fake, n_rows):
    """Mimics the exact schema of loan_data_20M.parquet"""
    data = []
    for i in range(n_rows):
        loan_amount = float(fake.random_int(min=5000, max=50000))
        interest_rate = random.uniform(0.05, 0.25)
        term_months = random.choice([12, 24, 36, 48, 60, 72, 84])

        data.append(
            {
                "loan_id": i,
                "customer_id": fake.random_int(min=100000, max=999999),
                "loan_amount": loan_amount,
                "interest_rate": interest_rate,
                "term_months": term_months,
                "credit_score": fake.random_int(min=300, max=850),
                "annual_income": float(fake.random_int(min=30000, max=200000)),
                "dti_ratio": random.uniform(0.1, 0.5),
                "number_of_dependents": random.randint(0, 5),
                "is_secured": fake.boolean(),
                "has_cosigner": fake.boolean(),
                "piti_coverage": fake.boolean(),
                "autopay_enabled": fake.boolean(),
                "monthly_payment": (loan_amount * (1 + interest_rate)) / term_months,
                "application_date": fake.date_time_between(start_date="-3y", end_date="now"),
                "loan_status": random.choice(
                    ["Current", "Fully Paid", "Late", "Default", "Grace Period"]
                ),
                "home_ownership": random.choice(["RENT", "MORTGAGE", "OWN", "ANY", "NONE"]),
                "region": random.choice(["West", "Midwest", "South", "Northeast"]),
                "grade": random.choice(["A", "B", "C", "D", "E", "F", "G"]),
                "full_name": fake.name(),
                "city": fake.city(),
                "address": fake.address().replace("\n", ", "),
                "employer_name": fake.company(),
            }
        )
    return pl.DataFrame(data)


def generate_mortgage_data(fake, n_rows):
    data = []
    for i in range(n_rows):
        data.append(
            {
                "mortgage_id": fake.uuid4(),
                "property_value": float(fake.random_int(min=100000, max=2000000)),
                "loan_amount": float(fake.random_int(min=80000, max=1800000)),
                "interest_rate": random.uniform(0.02, 0.08),
                "zip_code": fake.zipcode(),
                "is_refinance": fake.boolean(),
                "occupancy_type": random.choice(["Primary", "Secondary", "Investment"]),
            }
        )
    return pl.DataFrame(data)


def main():
    parser = argparse.ArgumentParser(description="Generate fake datasets for profiling benchmarks.")
    parser.add_argument(
        "--type",
        type=str,
        default="loan",
        choices=["loan", "bank", "population", "legacy_loan", "mortgage"],
        help="Type of data to generate",
    )
    parser.add_argument("--rows", type=int, default=100000, help="Number of rows to generate")
    parser.add_argument(
        "--output",
        type=str,
        default="/tmp/ibis-profiling/fake_data.parquet",
        help="Output path (parquet)",
    )

    args = parser.parse_args()
    fake = Faker()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    print(f"Generating {args.rows} rows of {args.type} data...")

    if args.type == "loan":
        df = generate_loan_data(fake, args.rows)
    elif args.type == "bank":
        df = generate_bank_data(fake, args.rows)
    elif args.type == "population":
        df = generate_population_data(fake, args.rows)
    elif args.type == "legacy_loan":
        df = generate_legacy_loan_data(fake, args.rows)
    else:
        df = generate_mortgage_data(fake, args.rows)

    print(f"Saving to {args.output}...")
    df.write_parquet(args.output)
    print("Done.")


if __name__ == "__main__":
    main()
