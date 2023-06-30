import pandas as pd
from datetime import datetime
import ssl

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

# Read the Planned Portfolio sheet directly without assigning it to a variable
df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

closing_date = datetime(2023, 6, 12)

# Calculate Remaining Lease Term (Days) using the vectorized operation
df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

# Calculate Age at Closing Date and Age at End of Contract
df_portfolio['Age at Closing Date'] = closing_date.year - df_portfolio['Manufacturing Date'].dt.year
df_portfolio['Age at End of Contract'] = df_portfolio['Age at Closing Date'] + df_portfolio['Remaining Lease Term (Days)'] // 365

# Use boolean indexing directly to filter rows with 'Sell' value
df_selling_units = df_portfolio[df_portfolio['Age at End of Contract'] > 15]

# Calculate the sum of 'RV' column using the filtered DataFrame
residual_value = df_selling_units['RV'].sum()

# Calculate total revenues under contract using vectorized operations
total_revenues = (df_portfolio['Remaining Lease Term (Days)']
                  * df_portfolio['Per Diem (Unit)']
                  * (df_portfolio['Contract Type'] != "Off Lease")).sum()

# Calculate remaining years, annual revenue, and remaining life revenues
df_portfolio['Remaining Years'] = 15 - df_portfolio['Age at Closing Date']
df_portfolio['Annual Revenue'] = df_portfolio['Per Diem (Unit)'] * 365
df_portfolio['Remaining Life Revenues'] = df_portfolio['Annual Revenue'] * df_portfolio['Remaining Years']

# Calculate total revenues under contract until Selling Age
total_revenues_life = df_portfolio['Remaining Life Revenues'].sum()

# Print the results
print(f"Total Revenues under contract: {total_revenues:,.2f} USD")
print(f"Residual Value: {residual_value:,.2f} USD")
print(f"Total Revenues under contract: {total_revenues + residual_value:,.2f} USD")
print(f"Total Revenues under contract: {total_revenues_life:,.2f} USD")