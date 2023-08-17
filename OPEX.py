from datetime import datetime

import numpy as np
import pandas as pd
import numpy_financial as npf


def cashflow_calculation(df_portfolio,
                         insurance_fees,
                         agency_fees,
                         handling_fees,
                         bad_debt,
                         discount_rate,
                         pd_ev):
    # Convert to date time
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])

    # Remaining contract days
    df_portfolio['Remaining Contract (days)'] = (
                df_portfolio['End Contract Date'] - df_portfolio['Closing Date']).dt.days
    df_portfolio['Contract Remaining Quarters'] = df_portfolio['Remaining Contract (days)'] / 90

    # Remaining economic life (only used for the Residual Value)
    df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)
    df_portfolio['Lifecycle Remaining Days'] = (df_portfolio['15 Years Date'] - df_portfolio['Closing Date']).dt.days
    df_portfolio['Lifecycle Remaining Quarters'] = df_portfolio['Lifecycle Remaining Days'] / 90

    # Economic life second contract
    df_portfolio['Remaining Days SC'] = (df_portfolio['15 Years Date'] - df_portfolio['End Contract Date']).dt.days
    df_portfolio['Remaining Days SC'] = [x if x > 0.0 else 0.0 for x in df_portfolio['Remaining Days SC']]
    df_portfolio['Remaining Quarters SC'] = df_portfolio['Remaining Days SC'] / 90

    # Create new columns for OPEX
    df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees
    df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
    df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']
    df_portfolio['Daily Cash Flow SC'] = df_portfolio['Per Diem (Unit)'] * (1 + pd_ev) - df_portfolio['Total OPEX']

    cols_to_keep = ['RV',
                    'Remaining Contract (days)',
                    'Contract Remaining Quarters',
                    'Lifecycle Remaining Days',
                    'Lifecycle Remaining Quarters',
                    'Remaining Days SC',
                    'Remaining Quarters SC',
                    'Daily Cash Flow',
                    'Daily Cash Flow SC']

    df_portfolio_Q = df_portfolio[cols_to_keep]

    groups = df_portfolio_Q['Lifecycle Remaining Quarters'].unique()
    df_grouped = df_portfolio_Q.groupby(by='Lifecycle Remaining Quarters')

    # 0 : Index, 1 : RV
    # 2 : Remaining Contract (days)
    # 3 : Contract Remaining Quarters
    # 4 : Lifecycle Remaining Days
    # 5 : Lifecycle Remaining Quarters
    # 6 : Remaining Days SC
    # 7 : Remaining Quarters SC
    # 8 : Daily Cash Flow
    # 9 : Daily Cash Flow S

    quarters_rev = np.zeros(15 * 4)
    for g in groups:
        for row in df_grouped.get_group(g).itertuples():
            # First Contract:
            array_values = np.full(int(row[3]), row[8] * 90)
            # Add RV first contract and remainder of last Quarter
            rv_rem = row[1] + (row[3] - int(row[3])) * 90 * row[8] * ((1 + discount_rate) ** (1 - row[3] - int(row[3])))
            array_values = np.append(array_values, rv_rem)
            # Second contract:
            array_values = np.append(array_values, np.full(int(row[7]), row[9] * 90))
            # Add RV second contract and remainder of last Quarter
            if row[7] == 0:
                rv_sc = 0
            elif row[7] != 0:
                rv_sc = row[1]
            rem = (row[7] - int(row[7])) * 90 * row[9] * (1 + discount_rate) ** (1 - (row[7] - int(row[7])))
            array_values = np.append(array_values, rv_sc + rem)

            array_values.resize(15 * 4, refcheck=False)

            quarters_rev = quarters_rev + array_values

    NPV = np.sum([x * 1 / (1 + discount_rate) ** (i + 1) for i, x in enumerate(quarters_rev)])
    ROI = (NPV / df_portfolio['Purchase Price'].sum() - 1) * 100

    cash_flows = -df_portfolio['Purchase Price']  # Initial investments are negative
    cash_flows = cash_flows + quarters_rev / (1 + 0.01794847) ** np.arange(1, 15 * 4 + 1)  # Add discounted cash flows

    return {'ROI': f"{ROI:,.2f} %",
            'NPV': f"{NPV:,.2f} USD"}

excel_path = '/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx'
df_portfolio = pd.read_excel(excel_path, sheet_name='Planned Portfolio')

dcf = cashflow_calculation(df_portfolio,
                           0.003,  # Insurance Fees
                           0.007,  # Agency Fees
                           0.002,  # Handling Fees
                           0.005,  # Bad debt
                           0.01794847,  # Discount Rate
                           0.06)  # Per Diem Evolution

print(dcf)
