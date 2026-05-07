import pandas as pd
from pathlib import Path

input_file = Path("sales-data.csv")
df = pd.read_csv(input_file)

# Remove invalid rows (important!)
df = df[df["sq__ft"] > 0]

# Compute price per square foot
df["price_per_sqft"] = df["price"] / df["sq__ft"]

# Calculate average
avg_price = df["price_per_sqft"].mean()

print("Average price per sqft:", avg_price)

# Filter below average
filtered_df = df[df["price_per_sqft"] < avg_price]

# Save output
filtered_df.to_csv("filtered_sales.csv", index=False)

print("Filtered CSV created successfully")