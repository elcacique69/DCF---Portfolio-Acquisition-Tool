import pandas as pd


def opex(closing_date, container_type, insurance_fees, agency_fees, bad_debt, handling_fees, storage_cost):
    """
    Calculates the total operating expenses (OPEX) for containers of a specified type within a portfolio based on:
    insurance fees, agency fees, bad debt, handling fees, and storage cost.

    Parameters:
    - closing_date (str): Date at which the function is supposed to calculate the OPEX "Expected format 'YYYY-MM-DD'".
    - Type (str): container type to calculate the OPEX for. Expected values are: "20'DC", "40'DC", "40'HC".
    - insurance_fees, agency_fees, bad_debt, handling_fees, storage_cost (float): Operational fees and costs.

    Returns:
    - total_opex (float): The total (OPEX) for the specified type of containers at the given closing date.
    """

    # Read data from Excel file into a DataFrame
    df_portfolio = pd.read_excel(
        '/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx', sheet_name='Planned Portfolio'
                                )
    df_portfolio = df_portfolio[df_portfolio['Type'] == container_type]

    # Convert dates to datetime
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])
    closing_date = pd.to_datetime(closing_date)

    # Calculate ages
    df_portfolio['Age at Closing Date'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days / 365
    df_portfolio['Age at Closing Date Days'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days
    df_portfolio['Lifecycle Remaining Years'] = 15 - df_portfolio['Age at Closing Date']
    df_portfolio['Lifecycle Remaining Days'] = 5475 - df_portfolio['Age at Closing Date Days']

    # Calculate remaining years, annual revenue, and remaining life revenues
    df_portfolio['Annual Revenue'] = df_portfolio['Per Diem (Unit)'] * 365
    annual_revenue = df_portfolio['Annual Revenue'].sum()

    # Calculate costs
    insurance_cost = annual_revenue * insurance_fees
    agency_cost = annual_revenue * agency_fees
    bad_debt_cost = annual_revenue * bad_debt
    handling_cost = annual_revenue * handling_fees

    # Calculate storage cost for Off lease containers
    df_off_lease = df_portfolio[df_portfolio['Current Status'] == 'Off Lease']
    number_of_units = len(df_off_lease)
    off_lease_period = 30
    total_storage_cost = number_of_units * (storage_cost * off_lease_period)

    total_opex = insurance_cost + agency_cost + bad_debt_cost + handling_cost + total_storage_cost

    return total_opex


TFC_OPEX = opex('2023-06-12', "20'DC",  0.003, 0.007, 0.005, 0.02, 0.55)
FFC_OPEX = opex('2023-06-12', "40'DC", 0.003, 0.007, 0.005, 0.02, 1.10)
FHC_OPEX = opex('2023-06-12', "40'HC", 0.003, 0.007, 0.005, 0.02, 1.10)
OPEX = TFC_OPEX + FFC_OPEX + FHC_OPEX

print(f"The total 20'DC OPEX: {TFC_OPEX:,.2f} USD")
print(f"The total 40'DC OPEX: {FFC_OPEX:,.2f} USD")
print(f"The total 40'HC OPEX: {FHC_OPEX:,.2f} USD")
print(f"The total OPEX: {OPEX:,.2f} USD")
