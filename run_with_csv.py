# run_with_csv.py
from example_pandas import DataProcessor
import sys

csv = sys.argv[1]
dp = DataProcessor(csv_path=csv)
df = dp.load() 

print(df)
print("\nSummary:\n", dp.summary())
print("\nCLV (simple, churn=0.2):", dp.compute_clv(arpu_column="arpu", churn_rate=0.2))
