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

def dcf_contract(df_portfolio, closing_date, insurance_fees, agency_fees, handling_fees,
                 bad_debt, management_fee, discount_rate, pd_ev, output_path, economic_life):

    # Convertir a formato de fecha
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])

    # Calcular el aniversario de 15 años
    df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)

    # Calcular las fechas de inicio y fin del Segundo Contrato (SC)
    df_portfolio['SC Start Date'] = df_portfolio['End Contract Date'] + pd.DateOffset(days=1)
    df_portfolio['SC End Date'] = df_portfolio['15 Years Date']

    # Calcular las columnas de gastos operativos (OPEX)
    df_portfolio['OPEX coefficient'] = insurance_fees + agency_fees + bad_debt + handling_fees + management_fee
    df_portfolio['OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['OPEX coefficient']
    df_portfolio['FC Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['OPEX']
    df_portfolio['SC Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] * (1 + pd_ev) - df_portfolio['OPEX']

    # Crear un nuevo DataFrame con la columna "Revenue Date"
    df_new = pd.DataFrame()

    # Inicializar el número en 1 y la fecha de inicio como 90 días después de la primera "Closing Date"
    t_0 = df_portfolio['Closing Date'].iloc[0] + pd.DateOffset(days=90)

    # Calcular las fechas de ingresos y agregarlas al nuevo DataFrame
    for i in range(economic_life):  # Usar la vida económica especificada en lugar de len(df_portfolio)
        df_new = df_new.append({'Number': i + 1, 'Revenue Date': t_0}, ignore_index=True)
        t_0 += pd.DateOffset(days=90)

    # Agregar la columna "Quarter Revenue" al DataFrame df_new
    df_new['Quarter Revenue'] = 0  # Inicializar la columna con valores cero

    # Iterar a través de las filas del DataFrame df_new
    for index, row in df_new.iterrows():
        revenue_date = row['Revenue Date']

        # Encontrar el índice correspondiente en df_portfolio para las fechas de ingresos
        idx = df_portfolio.index[df_portfolio['Closing Date'] <= revenue_date][-1]

        # Comparar fechas y calcular "Quarter Revenue" en función de las condiciones
        if df_portfolio['SC Start Date'][idx] > revenue_date:
            df_new.at[index, 'Quarter Revenue'] = df_portfolio['FC Daily Cash Flow'][idx] * 90
        else:
            df_new.at[index, 'Quarter Revenue'] = df_portfolio['SC Daily Cash Flow'][idx] * 90

    # Calcular NPV y agregarlo como una nueva columna
    df_new['NPV'] = \
        df_new['Quarter Revenue'] / (1 + discount_rate) ** (df_new.index // 4)

    # Calcular ROI
    npv = df_new['NPV'].sum()
    investment = df_portfolio['Purchase Price'].sum()
    roi = ((npv - investment) / investment) * 100

    # Calcular TIR
    cash_flows = df_new['NPV'].tolist()  # Usar valores de NPV para el cálculo de la TIR
    irr = npf.irr(cash_flows)

    # Exportar los ingresos trimestrales a Excel utilizando un administrador de contexto
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df_new.to_excel(writer, sheet_name='Quarterly Revenue', index=False)

    return {'ROI': f"{roi:.2f} %", 'NPV': f"{npv:,.2f} USD", 'IRR': f"{irr:,.2f} %"}

total_revenues = (df_portfolio['Remaining Lease Term (Days)']
                  * df_portfolio['Per Diem (Unit)']
                  * (df_portfolio['Contract Type'] != "Off Lease")).sum()




# OPEX

print(f"Total Revenues under contract: {total_revenues:,.2f} USD")


def storage_cost(row, days_off_lease):
    """
    Function Name: storage_cost

Parameters:

row (dict): A dictionary containing details about the unit, with keys 'Current Status' and 'Type'. The 'Current Status'
key is expected to have a value of 'Off Lease' or another status, and the 'Type' key should have a value such as "20'DC"
to determine the type of the unit.

off_lease_days (int or float): The number of days the unit has been off-lease. This value is multiplied by a rate to
calculate the storage cost.

Returns:

float: The storage cost for the given unit. If the 'Current Status' is 'Off Lease', the cost is calculated based on the
'Type' and the number of off_lease_days. If the unit's type is "20'DC", the cost is 0.55 times off_lease_days. For other
types, the cost is 1.10 times off_lease_days. If the 'Current Status' is not 'Off Lease', the function returns 0.
Description:
The storage_cost function calculates the storage cost for a given unit based on its current status and type. If the unit
is off-lease, the cost is computed using a specific rate depending on the type, multiplied by the number of days
off lease. If the unit is not off-lease, the function returns 0, indicating no storage cost.

    """
    if row['Current Status'] == 'Off Lease':
        if row['Type'] == "20'DC":
            return 0.55 * days_off_lease
        else:
            return 1.10 * days_off_lease
    else:
        return 0





df_portfolio['Storage Cost'] = df_portfolio.apply(lambda row: storage_cost(row, off_lease_days), axis=1)
