import pandas as pd

# Import Data Set
df_portfolio = \
    pd.read_excel('/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx',
                  sheet_name='Planned Portfolio')

# Constants
closing_date = pd.Timestamp('2023-06-12')
insurance_fees = 0.003
agency_fees = 0.007
bad_debt = 0.005
handling_fees = 0.002
discount_rate = 0.0175

# Revenues
df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)
df_portfolio['Lifecycle Remaining Days'] = df_portfolio['15 Years Date'] - closing_date
df_portfolio['Lifecycle Remaining Quarters'] = df_portfolio['Lifecycle Remaining Days'].dt.days / 90

# OPEX
df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees
df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']

# Repayment Installment
repayment = df_portfolio['Purchase Price'].sum() * 0.0125

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
            'Debt Repayment': repayment,
            'Total Revenue with RV': revenue_in_quarter + rv_value
        })

# Create a DataFrame with the quarterly data
df_quarterly = pd.DataFrame(quarterly_data)

# Group by quarter and sum the revenue and RV
quarterly_revenue = \
    df_quarterly.groupby('Quarter').agg({'Revenue': 'sum', 'RV': 'sum', 'Total Revenue with RV': 'sum'}).reset_index()

# Calculate NPV and add it as a new column
quarterly_revenue['NPV'] = \
    quarterly_revenue['Total Revenue with RV'] / (1 + discount_rate) ** quarterly_revenue['Quarter']

# Calculate ROI
investment = df_portfolio['Purchase Price'].sum()
roi = (quarterly_revenue['NPV'].sum() - investment) / investment * 100

print(investment)

print(f'The ROI is: {roi:,.2f} %')

# Export the quarterly revenue to Excel
quarterly_output_path = '/Users/carlosjosegonzalezacevedo/Downloads/Quarterly_Revenue.xlsx'
quarterly_revenue.to_excel(quarterly_output_path, index=False)
