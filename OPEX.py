import pandas as pd

def opex(closing_date,
               Type,
               insurance_fees, 
               agency_fees,
               bad_debt, 
               handling_fees, 
               storage_cost
               ):
    
    """
    Calculates the total operating expenses (OPEX) for containers of a specified type within a portfolio based on various factors
    such as insurance fees, agency fees, bad debt, handling fees, and storage cost.

    Parameters:
    - closing_date (str): The date at which the function is supposed to calculate the OPEX. Expected format 'YYYY-MM-DD'.
    - Type (str): The type of containers to calculate the OPEX for. Expected values are container types like "20'DC", "40'DC", "40'HC".
    - insurance_fees, agency_fees, bad_debt, handling_fees (float): Different types of fees and costs associated with the containers. 
      These values are expected to be in a decimal form representing the fraction of the life cycle revenues each fee takes up.
    - storage_cost (float): The daily storage cost for a single container that is off lease.

    Returns:
    - total_opex (float): The total operating expenses (OPEX) for the specified type of containers at the given closing date.
    """
    
    # Read data from Excel file into a DataFrame
    df_portfolio = pd.read_excel('/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx', sheet_name='Planned Portfolio')

    # Filter the data to only include specific type of containers
    df_portfolio = df_portfolio[df_portfolio['Type'] == Type]

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

    # Calculate costs

    ## INSURANCE FEE ##
    insurance_cost = life_cycle_revenues * insurance_fees

    ## AGENCY FEES ##
    agency_cost = life_cycle_revenues * agency_fees

    ## BAD DEBT ##
    bad_debt_cost = life_cycle_revenues * bad_debt

    ## HANDLING COSTS ##
    handling_cost = life_cycle_revenues * handling_fees

    ## STORAGE COSTS ##

    # Calculate Storage cost for Off lease containers
    df_off_lease = df_portfolio[df_portfolio['Current Status'] == 'Off Lease']
    number_of_units = len(df_off_lease)
    off_lease_period = 30
    total_storage_cost = number_of_units * (storage_cost * off_lease_period)

    total_opex = insurance_cost + agency_cost + bad_debt_cost + handling_cost + total_storage_cost

    return(total_opex)


TFC_OPEX = opex('2023-06-12', "20'DC",  0.003, 0.007, 0.005, 0.02, 0.55)
FFC_OPEX = opex('2023-06-12', "40'DC", 0.003, 0.007, 0.005, 0.02, 1.10)
FHC_OPEX = opex('2023-06-12', "40'HC", 0.003, 0.007, 0.005, 0.02, 1.10)
OPEX = TFC_OPEX + FFC_OPEX + FHC_OPEX


print(f"The total 20'DC OPEX: {TFC_OPEX:,.2f} USD")
print(f"The total 40'DC OPEX: {FFC_OPEX:,.2f} USD")
print(f"The total 40'HC OPEX: {FHC_OPEX:,.2f} USD")
print(f"The total OPEX: {OPEX:,.2f} USD")