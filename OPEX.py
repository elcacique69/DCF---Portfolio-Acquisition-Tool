from datetime import datetime
import pandas as pd

# Import Data Set
df_portfolio = \
    pd.read_excel('/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx',
                  sheet_name='Planned Portfolio')


def dcf_cashflow(closing_date,
                 insurance_fees,
                 agency_fees,
                 handling_fees,
                 bad_debt,
                 discount_rate,
                 output_path):

    # Create new columns for REVENUES
    df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)
    df_portfolio['Lifecycle Remaining Days'] = df_portfolio['15 Years Date'] - closing_date
    df_portfolio['Lifecycle Remaining Quarters'] = df_portfolio['Lifecycle Remaining Days'].dt.days / 90

    # Create new columns for OPEX
    df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees
    df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
    df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']

    # Create a list to contain the data for the quarters
    quarterly_data = []

    # Iterate through each row in the original DataFrame
    for index, row in df_portfolio.iterrows():
        for quarter in range(1, int(row['Lifecycle Remaining Quarters']) + 1):
            # Calculate the days in the quarter
            days_in_quarter = min(max(row['Lifecycle Remaining Days'].days - 90 * (quarter - 1), 0), 90)

            # Calculate the revenue for the quarter
            revenue_in_quarter = days_in_quarter * row['Daily Cash Flow']

            # Add RV value if it's the last quarter for the container
            rv_value = row['RV'] if quarter == int(row['Lifecycle Remaining Quarters']) else 0

            # Add the row to the quarterly data set
            quarterly_data.append({
                'Quarter': quarter,
                'Days in Quarter': days_in_quarter,
                'Revenue': revenue_in_quarter,
                'RV': rv_value,
                'Total Revenue with RV': revenue_in_quarter + rv_value
            })

    # Create a DataFrame with the quarterly data
    df_quarterly = pd.DataFrame(quarterly_data)

    # Group by quarter and sum the revenue and RV
    quarterly_revenue = \
        df_quarterly.groupby('Quarter').agg(
            {'Revenue': 'sum', 'RV': 'sum', 'Total Revenue with RV': 'sum'}).reset_index()

    # Calculate NPV and add it as a new column
    quarterly_revenue['NPV'] = \
        quarterly_revenue['Total Revenue with RV'] / (1 + discount_rate) ** quarterly_revenue['Quarter']

    # Calculate ROI
    investment = df_portfolio['Purchase Price'].sum()
    roi = (quarterly_revenue['NPV'].sum() - investment) / investment * 100

    # Export the quarterly revenue to Excel
    quarterly_revenue.to_excel(output_path, index=False)

    return {'ROI': f"{roi:,.2f} %"}


def storage_cost(row, days_off_lease):
    if row['Current Status'] == 'Off Lease':
        if row['Type'] == "20'DC":
            return 0.55 * days_off_lease
        else:
            return 1.10 * days_off_lease
    else:
        return 0


dcf = dcf_cashflow(datetime.strptime('2023-06-30', '%Y-%m-%d'),
                   0.003,
                   0.007,
                   0.002,
                   0.005,
                   0.01794847,
                   "/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/DCF_QRev.xlsx")
print(dcf)
