# Library
import pandas as pd

# load data frame
file_path = '/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Coorelation.xlsx'
df = pd.read_excel(file_path)

# Calculate the PD Change
df["PD Change"] = df["PD"].diff()

# Select columns for correlation calculation
columns_for_correlation = [
    "PD Change",
    "Used Containers Price",
    "New Container Price",
    "Replacement",
    "Operating Ratio",
    "World GDP"
]

# Calculate correlation matrix
correlation_with_pd_change = df[columns_for_correlation].corr()

print(correlation_with_pd_change)
