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
    ## 1) CONCENTRATION COVENANT:
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
    ## 2) ADVANCE RATE COVENANT:
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
    ## 3) AGE COVENANT ######################
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
        covenant_weight_avg_age = "No Nbv weverage wieghted age breach"


    #########################################
    ## 4) 
    #########################################

    



    return {'covenant_concentration':dict_concentration_breach,
            'covenant_advance_rate': covenant_advance_rate,
            'covenant_weight_avg_age': covenant_weight_avg_age}



