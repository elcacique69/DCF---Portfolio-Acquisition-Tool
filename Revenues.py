# Revenues
# Import the necessary libraries
import pandas as pd # Data manipulation and analysis library
import ssl # Provides SSL support for secure connections
from datetime import datetime # Date time library

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

# Define the URL of the Excel file to be read
xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

# Read the Excel file into DataFrames
df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

# Closing Date
closing_date = 2023,6,12

# New Remaining lease term in days
df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

# Filter leased equipment in an Data Frame
df_leased_equipment = df_portfolio[df_portfolio['Contract Type'] != "Off Lease"]

# New collumn for Contract Revenues
df_leased_equipment['Contract Revenues'] = df_leased_equipment['Remaining Lease Term (Days)'] * df_leased_equipment['Per Diem (Unit)']

# Calculate the total revenues for the contracts
total_revenues = df_leased_equipment['Contract Revenues'].sum()

print(total_revenues)