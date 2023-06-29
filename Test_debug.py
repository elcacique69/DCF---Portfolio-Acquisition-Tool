# Import the necessary libraries
import ssl # Provides SSL support for secure connections
import pandas as pd # Data manipulation and analysis library
import numpy as np # Numerical computing library
from tabulate import tabulate # Creates formatted tables
import matplotlib.pyplot as plt # Data visualization library
from datetime import datetime, timedelta # Date and time handling
import quandl # Access to financial and economic data
from openpyxl import load_workbook # Load and edit Excel workbooks
import xlsxwriter

# Disable SSL verification for HTTPS connections
ssl._create_default_https_context = ssl._create_unverified_context

# Define the URL of the Excel file to be read
xlsx_url = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"

# Read the Excel file into DataFrames
df_portfolio = pd.read_excel(xlsx_url, sheet_name="Planned Portfolio")
df_updated_asset_register = pd.read_excel(xlsx_url, sheet_name="Updated Asset Register")
df_debt = pd.read_excel(xlsx_url, sheet_name="Debt")

# CONCENTRATION COVENANT
# Calculate the sum of 'NBV' for the updated asset register
updated_asset_register_nbv = df_updated_asset_register['NBV'].sum()

# Define the list of Lessees and their concentration thresholds
lessees = {
    'MSC': 30,
    'MAERSK': 30,
    'CMA': 30,
    'COSCOMERCU': 30,
    'HAPAG': 30,
    'EVERGREEN': 30,
    'ONE': 30,
    'ZIM': 15,
    'MTT SHIP': 10,
    'SITC': 10
}

# Iterate over each Lessee and check their NBV concentration
for lessee, threshold in lessees.items():
    # Filter the DataFrame for rows where 'Lessee' is the current Lessee
    lessee_df = df_updated_asset_register[df_updated_asset_register['Lessee'] == lessee]

    # Calculate the sum of 'NBV' for the current Lessee
    nbv_sum = lessee_df['NBV'].sum() / updated_asset_register_nbv * 100

    # Print the sum of 'NBV' for the current Lessee
    print(f"NBV concentration for {lessee}: {nbv_sum:,.2f}%")

    # Check if the NBV concentration exceeds the threshold
    if nbv_sum > threshold:
        print(f"BREACH: {lessee} NBV concentration above {threshold}%!")

# Check if there were any concentration breaches
if all(nbv_sum <= threshold for lessee, threshold in lessees.items()):
    print("No concentration breaches have been observed.")


# Advance Rate
advance_rate = 65  # Verify at each Drawdown

# Updated debt
updated_debt = df_portfolio['Purchase Price'].sum() + df_debt['Drawdown'].sum()

# Calculate the closing advance rate as a percentage
closing_advance_rate = updated_debt / updated_asset_register_nbv * 100

# Check if the closing advance rate breaches the specified threshold
if closing_advance_rate > advance_rate:
    print(f"BREACH: The Advance Rate ({closing_advance_rate:,.2f}%) is above ({advance_rate:,.2f}%)")
else:
    print(f"No Advance Rate breaches (Advance Rate {closing_advance_rate:,.2f}%)")

# AGE COVENANT

# This is when the Closing takes place 
closing_date = datetime(2023, 6, 12)  # Set the closing date YYYY/MM/DD

# Convert the "Manufacturing Date" column to datetime if it's not already in datetime format
df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])

# Calculate the age for each container row
df_portfolio['Age'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days

# Calculate the weighted age using the "Age" and "Purchase Price" columns
df_portfolio['Weighted Age'] = df_portfolio['Age'] * df_portfolio['Purchase Price']

# Calculate the weighted average age
weighted_average_age = df_portfolio['Weighted Age'].sum() / df_portfolio['Purchase Price'].sum() / 365

# Print the weighted average age
print(f"No Weighted NBV Average Age breaches (Age {weighted_average_age:.2f} years)")

# Check if the weighted average age is above 9 and print a message
if weighted_average_age > 9:
    print("BREACH: The weighted average age is above 9 years.")

# NBV BY CEU

# New TEU in the updated Asset Register (Planned Portfolio + Asset Register)
updated_ceu = df_updated_asset_register['CEU'].sum()

# Purchase Price for each TEU
ceu_purchase_price = updated_asset_register_nbv / updated_ceu

# Verify if the CEU Purchase Price is above threshold
if ceu_purchase_price > 2900:
    print("BREACH: in contract the CEU price must be below 2900 USD")
else:
    print(f"No CEU Purchase Price breaches (CEU price {ceu_purchase_price:,.2f} USD)")

# MANUFACTURER COVENANT

# List of Acceptable Manufacturer
manufacturer_list = ["CIMC", "CXIC", "Maersk", "Singamas", "DFIC", "Fuwa", "Hyundai", "Pan Ocean", "Maristar", "FUWA"]

# Data Frame of non manufacturer
df_not_manuf = df_portfolio[~df_portfolio['Manufacturer'].isin(manufacturer_list)]

# Export non-matching containers to Excel
if not df_not_manuf.empty:
    export_path = "/Users/carlosjosegonzalezacevedo/Documents/02_NEOMA/01_Thesis/DCF Container portfolio acquisition model/DCF---Portfolio-Acquisition-Tool/containers_wrong_manufacturer.xlsx"
    sheet_name = "Wrong Manufacturer List"
    df_not_manuf.to_excel(export_path, index=False, sheet_name=sheet_name)
    print(f"BREACH: Non-matching containers exported to: {export_path} (Sheet: {sheet_name})")
else:
    print("No Manufacturer breaches have been observed")

# AVERAGE REMAINING LEASE TERM

# Filter containers manufactured after 2019
df_new_containers = df_portfolio[df_portfolio['Vintage'] > 2019].copy()

# Calculate remaining lease term
closing_date = datetime.now()  # Assuming the closing_date is the current date
df_new_containers['Remaining Lease Term'] = (df_new_containers['End Contract Date'] - closing_date).dt.days

# Calculate weighted average remaining lease term
weighted_average = (df_new_containers['Remaining Lease Term'] * df_new_containers['Purchase Price']).sum() / df_new_containers['Purchase Price'].sum()

# Verify if the CEU Purchase Price is above threshold
if weighted_average < 5:
    print("BREACH: the minimum weighted remaining lease term for equipment manufactured after 2019 must be 5 years")
else:
    print(f"No Containers Manufactured after 2019 remaining lease term breaches (Avg Remaing Lease Term {weighted_average:,.2f} years)")

# FINANCE LEASE CONCENTRATION

# Data Frame of Finance Lease Lessees
df_finance_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Finance Lease"]

# Calculate the NBV of Finance Leases
finance_lease_nbv = df_finance_lease['NBV'].sum()

# Calculates the NBV proportion of finance leases
finance_lease_proportion = finance_lease_nbv / updated_asset_register_nbv * 100

# Verify if the finance lease proportion is above threshold
if finance_lease_proportion > 30:
    print("BREACH: The Finance Lease proportion needs to be below 30%")
else:
    print(f"No Finance lease proportion breaches (Proportion {finance_lease_proportion:,.2f}%)")

# OFF Lease Proportion

# Data Frame of Off Lease Containers
df_off_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Off Lease"]

# Calculates the NBV of Off Lease containers
off_lease_nbv = df_off_lease['NBV'].sum()

# Calculates the Off Lease NBV proportion
off_lease_proportion = off_lease_nbv / updated_asset_register_nbv * 100

# Verify if the Off Lease proportion is above threshold
if off_lease_proportion > 5:
    print("BREACH: The Off Lease proportion needs to be below 5%")
else:
    print(f"No Off lease proportion breaches (Proportion {off_lease_proportion:,.2f}%)")

# Specify the export file path for the new Excel file
export_path_off_leased = "/Users/carlosjosegonzalezacevedo/Documents/02_NEOMA/01_Thesis/DCF Container portfolio acquisition model/off_Lease_List.xlsx"

# Create a sample DataFrame for the Dashboard sheet
dashboard_data = {
    'Metric': ['Total NBV of non-leased equipment', 'NBV proportion of non-leased equipment'],
    'Value': [off_lease_nbv, off_lease_proportion]
}

# Calculate and add the sum of Purchase Price for each container type
container_types = ["20'DC", "40'DC", "40'HC"]
container_sum_data = []
for container_type in container_types:
    df_container_type = df_off_lease[df_off_lease['Type'] == container_type]
    sum_purchase_price = df_container_type['NBV'].sum()
    container_sum_data.append({'Metric': f'{container_type} NBV', 'Value': sum_purchase_price})

# Data Frame for the Container Type sum
df_container_type_sum = pd.DataFrame(container_sum_data)

# Data Frame for the new sheet called "Dashboard"
df_dashboard = pd.DataFrame(dashboard_data)

# Create a new Excel file
writer = pd.ExcelWriter(export_path_off_leased, engine='xlsxwriter')

# Write the DataFrames to the respective sheets
df_off_lease.to_excel(writer, sheet_name='Non Leased Equipment', index=False)
df_dashboard.to_excel(writer, sheet_name='Dashboard', index=False)

df_container_type_sum.to_excel(writer, sheet_name='Dashboard', startrow=df_dashboard.shape[0]+2, index=False)

writer.save()

# Revuenues under contract

df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])

df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

total_revenues = (df_portfolio['Remaining Lease Term (Days)']
                  * df_portfolio['Per Diem (Unit)']
                  * (df_portfolio['Contract Type'] != "Off Lease")).sum()

print(f"Total Revenues under contract: {total_revenues:,.2f} USD")

# OPEX