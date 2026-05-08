from pathlib import Path

import pandas as pd


def run_csv_filter(input_file: Path, output_file: Path) -> None:
    df = pd.read_csv(input_file)

    # Keep only valid rows before price-per-sqft calculation.
    df = df[df["sq__ft"] > 0]
    df["price_per_sqft"] = df["price"] / df["sq__ft"]
    avg_price = df["price_per_sqft"].mean()
    filtered_df = df[df["price_per_sqft"] < avg_price]
    filtered_df.to_csv(output_file, index=False)

    print("Average price per sqft:", avg_price)
    print(f"Filtered CSV created successfully at {output_file}")


if __name__ == "__main__":
    run_csv_filter(input_file=Path("sales-data.csv"), output_file=Path("filtered_sales.csv"))