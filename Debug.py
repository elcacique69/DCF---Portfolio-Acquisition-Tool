import pandas as pd
import numpy as np
import numpy_financial as npf

def cash_flow(path_portfolio,
              insurance_fees,
              agency_fees,
              handling_fees,
              bad_debt,
              managment_fee,
              sell_fee,
              rv_ev,
              wacc
              ):
    
    # Load Data Frame with portfolio data
    df_portfolio = pd.read_excel(path_portfolio, sheet_name='Planned Portfolio')

    ### NBV AT END OF CONTRACT ###

    # Establish RV for units, it's for calculate the portfolio value (NBV)
    container_mapping = {
        "20'DC": 1100 * (1 + rv_ev),
        "40'DC": 1500 * (1 + rv_ev),
        "40'HC": 1700 * (1 + rv_ev)
    }

    df_portfolio['RV'] = df_portfolio['Type'].apply(lambda x: container_mapping.get(x, 0))

    # FORMAT: make sure that are on datetime format
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])

    # NEW COLUMN: calculate Depreciation Period and Unit Age
    df_portfolio['Depreciation Period (Days)'] = (df_portfolio['End Contract Date'] - df_portfolio['Closing Date']).dt.days
    df_portfolio['Age (Closing)'] = (df_portfolio['Closing Date'] - df_portfolio['Manufacturing Date']).dt.days / 365

    # Function for Daily Depreciation
    def depreciation_daily(row):
        if row['Purchase Price'] == row['RV']:
            return 0
        elif row['Age (Closing)'] > 13 and row['Purchase Price'] > row['RV']:
            depreciation_amount = row['Purchase Price'] - row['RV']
            depreciation_days = (row['End Contract Date'] - row['Closing Date']).days
            daily_depreciation = depreciation_amount / depreciation_days
            return daily_depreciation
        elif row['Age (Closing)'] < 13 and row['Purchase Price'] > row['RV']:
            depreciation_amount = row['Purchase Price'] - row['RV']
            date_13_years = row['Manufacturing Date'] + pd.DateOffset(years=13)
            depreciation_days = (date_13_years - row['Closing Date']).days
            daily_depreciation = depreciation_amount / depreciation_days
            return daily_depreciation
        else:
            return 0
        
    # NEW COLUMN: Daily Depreciation, Total Depreciation, NBV at end of contract
    df_portfolio['Daily Depreciation'] = df_portfolio.apply(depreciation_daily, axis=1)
    df_portfolio['Total Depreciation'] = np.maximum(0, np.minimum(df_portfolio['Daily Depreciation'] * df_portfolio['Depreciation Period (Days)'], df_portfolio['Purchase Price'] - df_portfolio['RV']))
    df_portfolio['NBV (Contract End Date)'] = df_portfolio['Purchase Price'] - df_portfolio['Total Depreciation']

    ### DAILY REVENUES ###

    # NEW VARIABLE: start_date, end_date, date_range
    start_date = df_portfolio['Closing Date'].mean() + pd.Timedelta(days=1)
    end_date = df_portfolio['End Contract Date'].max()
    date_range = pd.date_range(start=start_date, end=end_date)

    # NEW DATA FRAME: df_revenues donde se hara la tabla de revenues
    df_revenues = pd.DataFrame({'Date': date_range})

    # Gross Leasing Revenues for rented units by date
    gross_leasing_revenues = []

    for date in df_revenues['Date']:
        valid_units = df_portfolio[df_portfolio['End Contract Date'] >= date]
        total_revenue = valid_units['Per Diem (Unit)'].sum()
        gross_leasing_revenues.append(total_revenue)

    # Revenues coming from units sells at the end of their contract
    selling_revenues = []
    
    for date in df_revenues['Date']:
        selling_units = df_portfolio[df_portfolio['End Contract Date'] == date]
        total_selling_revenue = selling_units['NBV (Contract End Date)'].sum()
        selling_revenues.append(total_selling_revenue)

    # NEW COLUMN: Row Number Daily Revenues
    df_revenues['Row Number'] = df_revenues.reset_index().index + 1
    df_revenues['Gross Leasing Revenues'] = gross_leasing_revenues

    # NEW COLUMN: Insurance Fees, Agency Fees, Handling Fees, Bad Debt, Management Fee
    df_revenues['Insurance Fees'] = df_revenues['Gross Leasing Revenues'] * insurance_fees
    df_revenues['Agency Fees'] = df_revenues['Gross Leasing Revenues'] * agency_fees
    df_revenues['Handling Fees'] = df_revenues['Gross Leasing Revenues'] * handling_fees
    df_revenues['Bad Debt'] = df_revenues['Gross Leasing Revenues'] * bad_debt
    df_revenues['Management Fee'] = df_revenues['Gross Leasing Revenues'] * managment_fee

    fees_columns = ['Insurance Fees', 'Agency Fees', 'Handling Fees', 'Bad Debt', 'Management Fee']
    df_revenues['Selling Revenues'] = selling_revenues
    df_revenues['Sells Fees'] = df_revenues['Selling Revenues'] * sell_fee

    df_revenues['Net Leasing Revenues'] = df_revenues['Gross Leasing Revenues'] - df_revenues[fees_columns].sum(axis=1) + df_revenues['Selling Revenues']
    df_revenues['NPV Leasing Revenues'] = df_revenues['Net Leasing Revenues'] / (1 + wacc) ** df_revenues['Row Number']

    # Export to Excel
    df_revenues.to_excel(r'C:\Users\CAG\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Revenues_Output.xlsx', index=False)

    # 1. Compute initial outlay
    initial_outlay = df_portfolio['Purchase Price'].sum() * -1

    # 2. Construct cash flows list
    cash_flows = [initial_outlay]
    cash_flows.extend(df_revenues['NPV Leasing Revenues'])

    # RATES: NPV (USD), ROI (%), IRR (%)
    portfolio_npv = df_revenues['NPV Leasing Revenues'].sum()
    portfolio_roi = (df_revenues['Net Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()) / df_portfolio['Purchase Price'].sum()
    portfolio_irr = npf.irr(cash_flows)

    return {'Portfolio NPV': portfolio_npv, 
            'Portfolio ROI': portfolio_roi,
            'Portfolio IRR': portfolio_irr,
            }

revenues = cash_flow(r'C:\Users\CAG\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Data_Set_Closing.xlsx', # Path Portfolio
                     0.003,      # Insurance Fees
                     0.007,      # Agency Fees
                     0.002,      # Handling Fees
                     0.005,      # Bad Debt
                     0.05,       # Management Fees
                     0.08,       # Sell Fee
                     0.06,       # Residual Value evolution
                     0.000149315 # WACC
                     )

print(revenues)
