from pathlib import Path

from csv_filter import run_csv_filter

def run_csv_filter_job() -> None:
    input_file = Path("sales-data.csv")
    output_file = Path("filtered_sales.csv")
    run_csv_filter(input_file=input_file, output_file=output_file)
