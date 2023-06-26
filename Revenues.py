# Revenues
# Import the necessary libraries
import pandas as pd # Data manipulation and analysis library
import ssl # Provides SSL support for secure connections

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

# Define the URL of the Excel file to be read
xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

# Read the Excel file into DataFrames
df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

df_leased_equipment = df_portfolio[df_portfolio['Contract Type'] != "Off Lease"]