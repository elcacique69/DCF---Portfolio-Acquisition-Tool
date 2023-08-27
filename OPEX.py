import pandas as pd
import pathlib
import os
import sys
from tabulate import tabulate

library_tools_path = str(pathlib.PurePath(os.getcwd()))
sys.path.append(library_tools_path)

path_portfolio = library_tools_path + '/Data_Set_Closing.xlsx'
export_path = library_tools_path + '/Off_Lease_Units.xlsx'

import Library_Portfolio_Tools as lpt

def off_lease_units(path_portfolio, export_path):
    # Read the portfolio Excel file into a DataFrame
    portfolio_df = pd.read_excel(path_portfolio)

    rows = len(portfolio_df)

    # Calculate the proportion of leased equipment
    leased = len(portfolio_df[portfolio_df["Current Status"] == "On lease"])
    equipment_leased = leased / rows
    equipment_not_leased = 1 - equipment_leased

    # Create a DataFrame with only non-leased equipment
    non_leased_df = portfolio_df[portfolio_df["Current Status"] == "Off Lease"]

    # Calculate the total NBV of non-leased equipment
    total_non_leased_nbv = non_leased_df["Purchase Price"].sum()

    # Calculate the total NBV of all equipment
    total_nbv = portfolio_df["Purchase Price"].sum()

    # Calculate the proportion of NBV of non-leased equipment to the total NBV
    non_leased_nbv_proportion = total_non_leased_nbv / total_nbv

    # Rest of your code remains the same...
    
    output = {
        "Speculative NBV": total_non_leased_nbv,
        "Speculative NBV Allocation within the Portfolio": non_leased_nbv_proportion
    }

    return output

off_lease_units_result = off_lease_units(path_portfolio, export_path)
print(off_lease_units_result)
