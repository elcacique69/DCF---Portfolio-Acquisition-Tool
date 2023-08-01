# Library

import pandas as pd

# Function used to calculate the OPEX of 20'DC containers during their economic life

def opex_20_DC (
          closing_date,
          insurance_percentage,
          agency_percentage,
          handling_percentage
          ):

    # Read data from Excel file into a DataFrame
    xl = pd.ExcelFile('/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx')

    # Portfolio to be acquired
    df_portfolio = xl.parse('Planned Portfolio')

    # Filter the data to only include 20'DC containers
    df_portfolio = df_portfolio[df_portfolio['Type'] == "20'DC"]

    closing_date = pd.to_datetime(closing_date)

    # Calculate the age for each container row in Years
    df_portfolio['Age at Closing Date'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days / 365

    # Calculate the age for each container row in Days
    df_portfolio['Age at Closing Date Days'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days

    # Calculates the Remaining Lifecycle Years
    df_portfolio['Lifecycle Remaining Years'] = 15 - df_portfolio['Age at Closing Date']

    # Calculate the Remaining Lifecycle Days
    df_portfolio['Lifecycle Remaining Days'] = 5475 - df_portfolio['Age at Closing Date Days']

    # Calculate remaining years, annual revenue, and remaining life revenues
    df_portfolio['Annual Revenue'] = df_portfolio['Per Diem (Unit)'] * 365
    df_portfolio['Life Cycle Revenues'] = df_portfolio['Annual Revenue'] * df_portfolio['Lifecycle Remaining Years']
    life_cycle_revenues = df_portfolio['Life Cycle Revenues'].sum()

    # Calculate Storage cost for Off lease containers
    # df_portfolio['Storage Cost'] = df_portfolio['Lifecycle Remaining Days'] * Storage_cost
    # Life_cycle_storage_cost = df_portfolio['Storage Cost'].sum()

    # Insurance cost x% of revenues
    insurance_cost = life_cycle_revenues * insurance_percentage

    # Agency Fees x% of revenues
    agency_cost = life_cycle_revenues * agency_percentage

    # Handlings cost x% of revenues
    handling_cost = life_cycle_revenues * handling_percentage
    
    return(life_cycle_revenues, insurance_cost, agency_cost, handling_cost)

revenues_OPEX = opex_20_DC(2023/6/12, 0.003, 0.007)

print(revenues_OPEX)