# Revenues
# Import the necessary libraries
import pandas as pd # Data manipulation and analysis library
import ssl # Provides SSL support for secure connections
from datetime import datetime # Date time library

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

# Define the URL of the Excel file to be read
xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

# Read the Excel file into DataFrame
df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

# Convert the closing date to a datetime object
closing_date = datetime(2023, 6, 12)

# Convert the 'End Contract Date' column to datetime if it's not already in the correct format
df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])

# New Remaining lease term in days
df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

# Filter leased equipment in a DataFrame
df_leased_equipment = df_portfolio[df_portfolio['Contract Type'] != "Off Lease"]

# New column for Contract Revenues
df_leased_equipment['Contract Revenues'] = df_leased_equipment['Remaining Lease Term (Days)'] * df_leased_equipment['Per Diem (Unit)']

# Calculate the total revenues for the contracts
total_revenues = df_leased_equipment['Contract Revenues'].sum()

print(f"Total Revenues under contract {total_revenues:,.2f}")

print("NUEVO")

import pandas as pd
from datetime import datetime

xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

closing_date = datetime(2023, 6, 12)

df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])

df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

total_revenues = (df_portfolio['Remaining Lease Term (Days)']
                  * df_portfolio['Per Diem (Unit)']
                  * (df_portfolio['Contract Type'] != "Off Lease")).sum()

print(f"Total Revenues under contract: {total_revenues:,.2f}")
