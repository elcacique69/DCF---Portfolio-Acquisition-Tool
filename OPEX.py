# Library
import pandas as pd

def opex_20_DC(closing_date, insurance_percentage, agency_percentage, handling_percentage, storage_cost):
    # Read data from Excel file into a DataFrame
    df_portfolio = pd.read_excel('/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx', sheet_name='Planned Portfolio')

    # Filter the data to only include 20'DC containers
    df_portfolio = df_portfolio[df_portfolio['Type'] == "20'DC"]

    # Convert dates to datetime
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])
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
    df_off_lease = df_portfolio[df_portfolio['Current Status'] == 'Off Lease']
    number_of_units = len(df_off_lease)
    off_lease_period = 30
    total_storage_cost = number_of_units * (storage_cost * off_lease_period)

    # Calculate costs
    insurance_cost = life_cycle_revenues * insurance_percentage
    agency_cost = life_cycle_revenues * agency_percentage
    handling_cost = life_cycle_revenues * handling_percentage

    return(life_cycle_revenues, insurance_cost, agency_cost, handling_cost, total_storage_cost)

revenues_OPEX = opex_20_DC('2023-06-12', 0.003, 0.007, 0.01, 0.55)

print(revenues_OPEX)
