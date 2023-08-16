from datetime import datetime
import pandas as pd

# Define the Excel path
excel_path = r'C:\Users\camil\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Data_Set_Closing.xlsx'


def dcf_cashflow(df_portfolio,
                 closing_date,
                 insurance_fees,
                 agency_fees,
                 handling_fees,
                 bad_debt,
                 discount_rate,
                 pd_ev,
                 output_path):

    # Convert to date time
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])

    # Remaining contract days
    df_portfolio['Remaining Contract (days)'] = df_portfolio['End Contract Date'] - closing_date
    df_portfolio['Contract Remaining Quarters'] = df_portfolio['Remaining Contract (days)'].dt.days / 90

    # Remaining economic life (only used for the Residual Value)
    df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)
    df_portfolio['Lifecycle Remaining Days'] = df_portfolio['15 Years Date'] - closing_date
    df_portfolio['Lifecycle Remaining Quarters'] = df_portfolio['Lifecycle Remaining Days'].dt.days / 90

    # Economic life second contract
    df_portfolio['Lifecycle Remaining Days SC'] = df_portfolio['15 Years Date'] - df_portfolio['End Contract Date']
    df_portfolio['Lifecycle Remaining Quarters SC'] = df_portfolio['Lifecycle Remaining Days SC'].dt.days / 90

    # Create new columns for OPEX
    df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees
    df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
    df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']
    df_portfolio['Daily Cash Flow SC'] = df_portfolio['Per Diem (Unit)']*(1+pd_ev) - df_portfolio['Total OPEX']

    # Create a list to contain the data for the quarters
    quarterly_contract_rev = []

    # Iterate through each row in the original DataFrame
    for index, row in df_portfolio.iterrows():
        for quarter in range(1, int(row['Contract Remaining Quarters']) + 1):
            # Calculate the days in the quarter
            days_in_quarter = min(max(row['Remaining Contract (days)'].days - 90 * (quarter - 1), 0), 90)
            days_in_quarter_SC = min(max(row['Lifecycle Remaining Days SC'].days - 90 * (quarter - 1), 0), 90)

            # Calculate the revenue for the quarter
            if days_in_quarter != 0:
                revenue_in_quarter = days_in_quarter * row['Daily Cash Flow']
            elif days_in_quarter == 0:
                revenue_in_quarter = days_in_quarter_SC * row['Daily Cash Flow SC']

            # Add the Residual Value if it's the last quarter for the container
            rv_value = row['RV'] if quarter == int(row['Lifecycle Remaining Quarters']) else 0

            # Add the row to the quarterly data set
            quarterly_contract_rev.append({
                'Quarter': quarter,
                'Days in Quarter': days_in_quarter,
                'Revenue': revenue_in_quarter,
                'RV': rv_value,
                'Total Revenue with RV': revenue_in_quarter + rv_value
            })

    # Create a DataFrame with the quarterly data
    df_quarterly = pd.DataFrame(quarterly_contract_rev)

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
    npv = quarterly_revenue['NPV'].sum()

    # Export the quarterly revenue to Excel
    quarterly_revenue.to_excel(output_path, index=False)

    return {'ROI': f"{roi:,.2f} %",
            'NPV': f"{npv:,.2f} USD"}


# Load the data
df_portfolio = pd.read_excel(excel_path, sheet_name='Planned Portfolio')

dcf_fc = dcf_cashflow(df_portfolio, datetime.strptime('2023-06-12', '%Y-%m-%d'), 0.003, 0.007, 0.002, 0.005, 0.01794847, 0.06,
                      r"C:\Users\camil\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Q_DCF.xlsx")
