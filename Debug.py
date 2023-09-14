import pandas as pd

def cash_flow(path_portfolio, insurance_fees, agency_fees, handling_fees, bad_debt, mng_fee, rv_ev, wacc):
    
    df_portfolio = pd.read_excel(path_portfolio, sheet_name='Planned Portfolio')

    container_mapping = {
        "20'DC": 1000 * (1 + rv_ev),
        "40'DC": 1200 * (1 + rv_ev),
        "40'HC": 1400 * (1 + rv_ev)
    }

    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])

    df_portfolio['RV'] = df_portfolio['Type'].apply(lambda x: container_mapping.get(x, 0))
    df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees + mng_fee
    df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
    df_portfolio['Remaining Contract (days)'] = (df_portfolio['End Contract Date'] - df_portfolio['Closing Date']).dt.days
    df_portfolio['Remaining Contract (months)'] = df_portfolio['Remaining Contract (days)'] / 30
    df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']

    months_nb = df_portfolio['Remaining Contract (months)'].max().astype(int)

    df_monthly_revenue = pd.DataFrame({'Month': range(1, months_nb+2),
                                   'Net Monthly Revenue': [0.0] * (months_nb+1),
                                   'NPV Monthly Revenue': [0.0] * (months_nb+1)})

    for month in range(1, months_nb+1):
        applicable_rows = df_portfolio[df_portfolio['Remaining Contract (months)'] >= month]
        df_monthly_revenue.at[month, 'Net Monthly Revenue'] += (applicable_rows['Daily Cash Flow'] * 30).sum()

        # Add residual value at the end of the contract
        end_of_contract_rows = df_portfolio[df_portfolio['Remaining Contract (months)'] == month]
        total_rv_for_month = end_of_contract_rows['RV'].sum()
        df_monthly_revenue.at[month, 'Net Monthly Revenue'] += total_rv_for_month
        df_monthly_revenue.at[month, 'RV Sales'] = total_rv_for_month  # Storing the total RV for the month

        # Compute NPV for that month
        df_monthly_revenue.at[month, 'NPV Monthly Revenue'] = df_monthly_revenue.at[month, 'Net Monthly Revenue'] / (1 + wacc) ** month

    revenues = df_monthly_revenue['Net Monthly Revenue'].sum()


    return revenues, df_monthly_revenue

revenues = cash_flow(r'C:\Users\CAG\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Data_Set_Closing.xlsx',
                     0.003, 0.007, 0.002, 0.005, 0.05, 0.06, 0.006666667)

print(revenues)
