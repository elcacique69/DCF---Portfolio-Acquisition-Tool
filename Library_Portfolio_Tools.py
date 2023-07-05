# Import the necessary libraries
import ssl # Provides SSL support for secure connections
import pandas as pd # Data manipulation and analysis library
import numpy as np # Numerical computing library
from tabulate import tabulate # Creates formatted tables
import matplotlib.pyplot as plt # Data visualization library
from datetime import datetime as dt, timedelta # Date and time handling
import quandl # Access to financial and economic data
from openpyxl import load_workbook # Load and edit Excel workbooks
#import xlsxwriter


# FUNCTION BANK COVENANTS:
def bank_covenants(
                    path_df,
                    ADVANCE_RATE,
                    closing_date,  
                    MINIMAL_AMOUNT=3000000.0, 
                    FACILITY=35000000.0
                ):
    
    """This function imports a data frame and recovers the most expensive containers

        path_df: Place in the computer where the df is
        minimal_amount: Covenant by default 3Mio
        facility: Covenant by default 35Mio 
    """
    
    # Import data
    df_portfolio = pd.read_excel(path_df, sheet_name="Planned Portfolio")
    df_updated_asset_register = pd.read_excel(path_df, sheet_name="Updated Asset Register")
    df_debt = pd.read_excel(path_df, sheet_name="Debt")

    ####### COVENANTS ########

    #########################################
    ## 1) CONCENTRATION COVENANT
    #########################################

    # Calculate the sum of 'NBV' for the updated asset register
    updated_asset_register_nbv = df_updated_asset_register['NBV'].sum()

    # Define the list of Lessees and their concentration thresholds
    dict_lessees = {
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
    for lessee, threshold in dict_lessees.items():
        # Filter the DataFrame for rows where 'Lessee' is the current Lessee
        df_lessee = df_updated_asset_register[df_updated_asset_register['Lessee'] == lessee]

        # Calculate the sum of 'NBV' for the current Lessee
        nbv_sum = df_lessee['NBV'].sum() / updated_asset_register_nbv * 100

        # Convenant test:
        if nbv_sum >= threshold:
            print(f"The leesse {lessee} is in breach for the contentration convenant {threshold}")
            dict_concentration_breach = {lessee:df_lessee}
        else:
            dict_concentration_breach = {}

    if dict_concentration_breach == {}:
        dict_concentration_breach = "No concentration convenant breach"


    #########################################
    ## 2) ADVANCE RATE COVENANT
    #########################################

    # Updated debt
    updated_debt = df_portfolio['Purchase Price'].sum() + df_debt['Drawdown'].sum()

    # Calculate the closing advance rate as a percentage
    closing_advance_rate = updated_debt / updated_asset_register_nbv * 100

    # Check if the closing advance rate breaches the specified threshold
    if closing_advance_rate > ADVANCE_RATE:
        covenant_advance_rate = f"BREACH: The Advance Rate ({closing_advance_rate:,.2f}%) is above ({ADVANCE_RATE:,.2f}%)"
    else:
        covenant_advance_rate = f"No Advance Rate breaches (Advance Rate {closing_advance_rate:,.2f}%)"

    #########################################
    ## 3) AGE COVENANT
    #########################################

    # AGE COVENANT
    # This is when the Closing takes place 

    # Convert the "Manufacturing Date" column to datetime if it's not already in datetime format
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])

    # Calculate the age for each container row
    df_portfolio['Age'] = (dt.strptime(closing_date, "%Y-%m-%d") - df_portfolio['Manufacturing Date']).dt.days

    # Calculate the weighted age using the "Age" and "Purchase Price" columns
    df_portfolio['Weighted Age (Years)'] = (df_portfolio['Age'] * df_portfolio['Purchase Price']/df_portfolio['Purchase Price'].sum()) / 365

    # Calculate the weighted average age
    weighted_average_age = df_portfolio['Weighted Age (Years)'].sum()

    # Check if the weighted average age is above 9 and print a message
    if weighted_average_age > 9:
        covenant_weight_avg_age = f"BREACH: The weighted average age {weighted_average_age:,.2f} of the portfolio is above 9 years."
    else:
        covenant_weight_avg_age = "No NBV weighted average age breach"


    #########################################
    ## 4) NBV by TEU (CEU)
    #########################################

    # New TEU in the updated Asset Register (Planned Portfolio + Asset Register)
    updated_ceu = df_updated_asset_register['CEU'].sum()

    # Purchase Price for each TEU
    ceu_purchase_price = updated_asset_register_nbv / updated_ceu

    # Verify if the CEU Purchase Price is above threshold
    if ceu_purchase_price > 2900:
        covenant_nbv_ceu = f"BREACH: The NBV by CEU is: {ceu_purchase_price:,.2f} USD. The limit is 2900 USD"
    else:
        covenant_nbv_ceu = f"No NBV by CEU breach: {ceu_purchase_price:,.2f} USD. The limit is 2900 USD"
    
    #########################################
    ## 6) MANUFACTURER COVENANT
    #########################################

    # List of Acceptable Manufacturer
    manufacturer_list = ["CIMC", 
                         "CXIC", 
                         "Maersk", 
                         "Singamas", 
                         "DFIC", 
                         "Fuwa", 
                         "Hyundai", 
                         "Pan Ocean", 
                         "Maristar", 
                         "FUWA"]

    # Data Frame of non manufacturer
    df_not_manuf = df_portfolio[~df_portfolio['Manufacturer'].isin(manufacturer_list)]

    # Export non-matching containers to Excel
    if not df_not_manuf.empty:
        export_path = "/Users/carlosjosegonzalezacevedo/Documents/02_NEOMA/01_Thesis/DCF Container portfolio acquisition model/DCF---Portfolio-Acquisition-Tool/containers_wrong_manufacturer.xlsx"
        sheet_name = "Wrong Manufacturer List"
        df_not_manuf.to_excel(export_path, index=False, sheet_name=sheet_name)
        covenant_manufacturer = f"BREACH: Non-matching containers exported to: {export_path} (Sheet: {sheet_name})"
    else:
        covenant_manufacturer = "No Manufacturer breaches have been observed"

    ###################################################################
    # 7) Average Remaining Lease Term: for containers built after 2019
    ###################################################################

    # Filter containers manufactured after 2019
    df_new_containers = df_portfolio[df_portfolio['Vintage'] > 2019].copy()

    # Convert closing_date to datetime
    closing_date = pd.to_datetime(closing_date)
    
    # Calculate remaining lease term
    df_new_containers['Remaining Lease Term'] = (df_new_containers['End Contract Date'] - closing_date).dt.days

    # Calculate weighted average remaining lease term
    weighted_average = (df_new_containers['Remaining Lease Term'] * df_new_containers['Purchase Price']).sum() / df_new_containers['Purchase Price'].sum()

    # Verify if the CEU Purchase Price is above threshold
    if weighted_average < 5:
        covenant_avg_lease = f"BREACH: the minimum weighted remaining lease term for equipment manufactured after 2019 must be 5 years. Actual RLT : {weighted_average:,.2f}"
    else:
        covenant_avg_lease = f"No Containers Manufactured after 2019 remaining lease term breaches (Avg Remaing Lease Term {weighted_average:,.2f} years)"

    ###################################################################
    # 8) Off Lease NBV portfolio concentration
    ###################################################################
    
    # Data Frame of Off Lease Containers
    df_off_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Off Lease"]

    # Calculates the NBV of Off Lease containers
    off_lease_nbv = df_off_lease['NBV'].sum()

    # Calculates the Off Lease NBV proportion
    off_lease_proportion = off_lease_nbv / updated_asset_register_nbv * 100

    # Verify if the Off Lease proportion is above threshold
    if off_lease_proportion > 5:
        covenant_offlease_concentration = f"BREACH: The Off Lease proportion needs to be below 5%. Actual : {off_lease_proportion:,.2f}"
    else:
        covenant_offlease_concentration = f"No Off lease proportion breaches (Proportion {off_lease_proportion:,.2f}%)"

    # Specify the export file path for the new Excel file
    export_path_off_leased = "/Users/carlosjosegonzalezacevedo/Documents/02_NEOMA/01_Thesis/DCF Container portfolio acquisition model/off_Lease_List.xlsx"

    # Create a sample DataFrame for the Dashboard sheet
    dashboard_data = {
    'Metric': ['Total NBV of non-leased equipment', 'NBV proportion of non-leased equipment'],
    'Value': [off_lease_nbv, off_lease_proportion]
    }

    ###################################################################
    # 9) Finance Lease NBV portfolio concentration
    ###################################################################

    # Data Frame of Finance Lease Lessees
    df_finance_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Finance Lease"]

    # Calculate the NBV of Finance Leases
    finance_lease_nbv = df_finance_lease['NBV'].sum()

    # Calculates the NBV proportion of finance leases
    finance_lease_proportion = finance_lease_nbv / updated_asset_register_nbv * 100

    # Verify if the finance lease proportion is above threshold
    if finance_lease_proportion > 30:
        covenant_financelease_concentration = f"BREACH: The Finance Lease proportion needs to be below 30%. Actual: {finance_lease_proportion:,.2f}"
    else:
       covenant_financelease_concentration = f"No Finance lease proportion breaches (Proportion {finance_lease_proportion:,.2f}%)"

    return {'4.a) Manufactured by an Acceptable Manufacturer': covenant_manufacturer,
            '4.b) NBV Weighted Average Age of such Equipment': covenant_weight_avg_age,
            '4.c) Average Remaining Lease Term of the such Equipment manufactured after 2019' : covenant_avg_lease,
            '4.d) Total Purchase Price by CEU': covenant_nbv_ceu,
            '5.19) Concentration Limits': dict_concentration_breach,
            'Advance Rate cheking': covenant_advance_rate,
            '5.13) OFF Lease portfolio NBV concentration' : covenant_offlease_concentration,
            '5.17) Finance Lease portfolio NBV concentration' : covenant_financelease_concentration}



