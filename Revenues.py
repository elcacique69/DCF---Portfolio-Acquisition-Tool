# Revenues
# Import the necessary libraries
import pandas as pd # Data manipulation and analysis library
import ssl # Provides SSL support for secure connections
from datetime import datetime # Date time library

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")

#Setting the closing date and converting the 'End Contract Date' column to datetime:
closing_date = datetime(2023, 6, 12)
df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])

# Calculating the remaining lease term in days
df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

# Calculating the total revenues under contract:
total_revenues = (df_portfolio['Remaining Lease Term (Days)']
                  * df_portfolio['Per Diem (Unit)']
                  * (df_portfolio['Contract Type'] != "Off Lease")).sum()

print(f"Total Revenues under contract: {total_revenues:,.2f}")

# Residual Value Sales
# Define the sale revenue values for each container type
container_revenues = {
    '20\'DC': 1100,
    '40\'DC': 1500,
    '40\'HC': 1700
}

# Sale revenue for containers when they are 15 years old
selling_age = 15

# Calculate the age at the closing date
df_portfolio['Age at Closing Date'] = closing_date - df_portfolio['Manufacturing Date']

# Calculate the age at the end of the contract
df_portfolio['Age at End of Contract'] = df_portfolio['Age at Closing Date'] + df_portfolio['Remaining Lease Term (Days)'] // 365

# Check if the age at the end of the contract is above 15 and set the value in the "Sell" column
df_portfolio['Sell'] = df_portfolio['Age at End of Contract'] > 15

# Calculate the total sale revenue for containers when they are 15 years old
total_sale_revenue = sum(df_portfolio[df_portfolio['Sell']][df_portfolio['Type'] == container_type]['Remaining Lease Term (Days)'] // 365 * container_revenues[container_type] for container_type in container_revenues)

for container_type in container_revenues:
    sale_revenue = (df_portfolio[df_portfolio['Sell']][df_portfolio['Type'] == container_type]['Remaining Lease Term (Days)'] // 365 * container_revenues[container_type]).sum()
    print(f"{container_type}: {sale_revenue:,.2f}")