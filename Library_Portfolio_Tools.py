#### Here we the...

import pandas as pd
import numpy as np
from tabulate import tabulate
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
import quandl
from datetime import datetime
from openpyxl import load_workbook


# FUNCTION BANK COVENANTS:


def bank_convenants(path_df,
                MIN_PRICE, 
                MINIMAL_AMOUNT=3000000.0, 
                FACILITY=35000000.0
                ):
    
    """This function imports a data frame and recovers the most expensive containers

        path_df: Place in the computer where the df is
        minimal_amount: Covenant by default 3Mio
        facility: Covenant by default 35Mio 
    """
    
    df_portfolio = pd.read_excel(path_df, sheet_name="Planned Portfolio")
    df_asset_register = pd.read_excel(path_df, sheet_name="Updated Asset Register")
    df_debt = pd.read_excel(path_df, sheet_name="Debt")

    # Calculate the Portfolio Purchase Price
    purchase_price = df_portfolio['Purchase Price'].sum()

    
    # Outstanding Facility Amount
    debt = df_debt['Drawdown'].sum()
    outstanding_facility = FACILITY - debt

    # If statement for Purchase Amount Covenant
    if purchase_price > MINIMAL_AMOUNT:
        if purchase_price <= outstanding_facility:
            warning_drowdown = "The Drawdown minimal amount is respected"
        else:
            warning_drowdown = "BREACH: The purchase amount exceeds the facility capacity."
    else:
        warning_drowdown = "BREACH: minimal amount for drawdown is 3,000,000.00 USD"

    ### Df test recupera los containers más caros
    df_containers_expensives = df_portfolio[df_portfolio['Purchase Price'] > MIN_PRICE]


    ### FALTA Agregar codigo


    manufacturer_list = ["CIMC", "Singamas", "Maersk", "Dong Fang", "CXI", "Seabox",
                     "China Shipping Container Lines (CSCL)", "Textainer Group Holdings Limited",
                     "COSCO Shipping Development", "Hoover Ferguson Group"]
    
    df_not_manuf = df_portfolio[~df_portfolio['Manufacturer'].isin(manufacturer_list)]

    return [df_portfolio, df_containers_expensives, warning_drowdown]
