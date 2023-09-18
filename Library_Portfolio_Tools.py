# Import the necessary libraries
import ssl # Provides SSL support for secure connections
import pandas as pd # Data manipulation and analysis library
import numpy as np # Numerical computing library
from tabulate import tabulate  # Creates formatted tables
import matplotlib.pyplot as plt  # Data visualization library
from datetime import datetime as dt, timedelta # Date and time handling
import quandl  # Access to financial and economic data
from openpyxl import load_workbook  # Load and edit Excel workbooks
import numpy_financial as npf
#import xlsxwriter


# FUNCTION BANK COVENANTS:
def bank_eligibility_check(
                           path_df,
                           ADVANCE_RATE,
                           closing_date,  
                           MINIMAL_AMOUNT=3000000.0, 
                           FACILITY=35000000.0
                        ):
    
    """This function imports a data frame and recovers the most expensive containers

        path_df: Place in the computer where the df is
        minimal_amount: Covenant by default 3Mio
        facility: Covenant by default 35Mio 
    """
    
    # Import data
    df_portfolio = pd.read_excel(path_df, sheet_name="Planned Portfolio")
    df_updated_asset_register = pd.read_excel(path_df, sheet_name="Updated Asset Register")
    df_debt = pd.read_excel(path_df, sheet_name="Debt")

    # Format dates:
    closing_date = dt.strptime(closing_date, "%Y-%m-%d")
    df_portfolio['Manufacturing Date'] = pd.to_datetime(df_portfolio['Manufacturing Date'])
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])


    ####### COVENANTS ########

    #########################################
    ## 1) CONCENTRATION COVENANT
    #########################################

    # Calculate the sum of 'NBV' for the updated asset register
    updated_asset_register_nbv = df_updated_asset_register['NBV'].sum()

    # Define the list of Lessees and their concentration thresholds
    dict_lessees = {
        'MSC': 30,
        'MAERSK': 30,
        'CMA': 30,
        'COSCOMERCU': 30,
        'HAPAG': 30,
        'EVERGREEN': 30,
        'ONE': 30,
        'ZIM': 15,
        'MTT SHIP': 10,
        'SITC': 10
    }


    # Iterate over each Lessee and check their NBV concentration
    for lessee, threshold in dict_lessees.items():
        # Filter the DataFrame for rows where 'Lessee' is the current Lessee
        df_lessee = df_updated_asset_register[df_updated_asset_register['Lessee'] == lessee]

        # Calculate the sum of 'NBV' for the current Lessee
        nbv_sum = df_lessee['NBV'].sum() / updated_asset_register_nbv * 100

        # Convenant test:
        if nbv_sum >= threshold:
            print(f"BREACH: The leesse {lessee} is in breach for the contentration convenant {threshold}")
            dict_concentration_breach = {lessee:df_lessee}
        else:
            dict_concentration_breach = {}

    if dict_concentration_breach == {}:
        dict_concentration_breach = "NO BREACH"


    #########################################
    ## 2) ADVANCE RATE COVENANT
    #########################################

    # Updated debt
    updated_debt = df_portfolio['Purchase Price'].sum() + df_debt['Drawdown'].sum()

    # Calculate the closing advance rate as a percentage
    closing_advance_rate = updated_debt / updated_asset_register_nbv * 100

    # Check if the closing advance rate breaches the specified threshold
    if closing_advance_rate > ADVANCE_RATE:
        covenant_advance_rate = f"BREACH: The Advance Rate ({closing_advance_rate:,.2f}%) is above ({ADVANCE_RATE:,.2f}%)"
    else:
        covenant_advance_rate = f"NO BREACH: Advance Rate {closing_advance_rate:,.2f}%"

    #########################################
    ## 3) AGE COVENANT
    #########################################

    # AGE COVENANT
    # This is when the Closing takes place 

    
    # Calculate the age for each container row
    df_portfolio['Age at Closing Date'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days / 365

    # Calculate the weighted age using the "Age" and "Purchase Price" columns
    df_portfolio['Weighted Age (Years)'] = df_portfolio['Age at Closing Date'] * df_portfolio['Purchase Price']/df_portfolio['Purchase Price'].sum()

    # Calculate the weighted average age
    weighted_average_age = df_portfolio['Weighted Age (Years)'].sum()

    # Check if the weighted average age is above 9 and print a message
    if weighted_average_age > 9:
        covenant_weight_avg_age = f"BREACH: The weighted average age {weighted_average_age:,.2f} of the portfolio is above 9 years."
    else:
        covenant_weight_avg_age = f"NO BREACH: weighted avg age {weighted_average_age:,.2f}"


    #########################################
    ## 4) NBV by TEU (CEU)
    #########################################

    # New TEU in the updated Asset Register (Planned Portfolio + Asset Register)
    updated_ceu = df_updated_asset_register['CEU'].sum()

    # Purchase Price for each TEU
    ceu_purchase_price = updated_asset_register_nbv / updated_ceu

    # Verify if the CEU Purchase Price is above threshold
    if ceu_purchase_price > 2900:
        covenant_nbv_ceu = f"BREACH: The NBV by CEU is: {ceu_purchase_price:,.2f} USD. The limit is 2900 USD"
    else:
        covenant_nbv_ceu = f"NO BREACH: NBV by CEU: {ceu_purchase_price:,.2f} USD."
    
    #########################################
    ## 6) MANUFACTURER COVENANT
    #########################################

    # List of Acceptable Manufacturer
    manufacturer_list = ["CIMC", 
                         "CXIC", 
                         "Maersk", 
                         "SINGAMAS", 
                         "DFIC", 
                         "Fuwa", 
                         "Hyundai", 
                         "Pan Ocean", 
                         "Maristar", 
                         "FUWA"]

    # Data Frame of non manufacturer
    df_not_manuf = df_portfolio[~df_portfolio['Manufacturer'].isin(manufacturer_list)]

    # Export non-matching containers to Excel
    if not df_not_manuf.empty:
        export_path = path_df.replace("Data_Set_Closing.xlsx", "containers_wrong_manufacturer.xlsx")
        sheet_name = "Wrong Manufacturer List"
        df_not_manuf.to_excel(export_path, index=False, sheet_name=sheet_name)
        covenant_manufacturer = f"BREACH: Non-matching containers exported to: {export_path} (Sheet: {sheet_name})"
    else:
        covenant_manufacturer = "NO BREACH: acceptable manufacturers"

    ###################################################################
    # 7) Average Remaining Lease Term: for containers built after 2019
    ###################################################################

    # Filter containers manufactured after 2019
    df_new_containers = df_portfolio[df_portfolio['Vintage'] > 2019].copy()
   
    # Calculate remaining lease term
    df_new_containers['Remaining Lease Term'] = ((df_new_containers['End Contract Date'] - closing_date).dt.days) / 365

    # Calculate weighted average remaining lease term
    weighted_average = (df_new_containers['Remaining Lease Term'] * df_new_containers['Purchase Price']).sum() / df_new_containers['Purchase Price'].sum()

    # Verify if the CEU Purchase Price is above threshold
    if weighted_average < 5:
        covenant_avg_lease = f"BREACH: the minimum weighted remaining lease term must be 5 years. Actual RLT : {weighted_average:,.2f}"
    else:
        covenant_avg_lease = f"NO BREACH: Avg Remaing Lease Term {weighted_average:,.2f} years"

    ###################################################################
    # 8) Off Lease NBV portfolio concentration
    ###################################################################
    
    # Data Frame of Off Lease Containers
    df_off_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Off Lease"]

    # Calculates the NBV of Off Lease containers
    off_lease_nbv = df_off_lease['NBV'].sum()

    # Calculates the Off Lease NBV proportion
    off_lease_proportion = off_lease_nbv / updated_asset_register_nbv * 100

    # Verify if the Off Lease proportion is above threshold
    if off_lease_proportion > 5:
        covenant_offlease_concentration = f"BREACH: The Off Lease proportion needs to be below 5%. Actual : {off_lease_proportion:,.2f}"
    else:
        covenant_offlease_concentration = f"NO BREACH: Off-Lease Proportion {off_lease_proportion:,.2f}%"

    # Specify the export file path for the new Excel file
    ### To replace for company folder on implementation 
    export_path_off_leased = path_df.replace("Data_Set_Closing.xlsx", "off_Lease_List.xlsx")

    # Create a sample DataFrame for the Dashboard sheet
    dashboard_data = {
    'Metric': ['Total NBV of non-leased equipment', 'NBV proportion of non-leased equipment'],
    'Value': [off_lease_nbv, off_lease_proportion]
    }

    ###################################################################
    # 9) Finance Lease NBV portfolio concentration
    ###################################################################

    # Data Frame of Finance Lease Lessees
    df_finance_lease = df_updated_asset_register[df_updated_asset_register['Lease Type'] == "Finance Lease"]

    # Calculate the NBV of Finance Leases
    finance_lease_nbv = df_finance_lease['NBV'].sum()

    # Calculates the NBV proportion of finance leases
    finance_lease_proportion = finance_lease_nbv / updated_asset_register_nbv * 100

    # Verify if the finance lease proportion is above threshold
    if finance_lease_proportion > 30:
        covenant_financelease_concentration = f"BREACH: The Finance Lease proportion needs to be below 30%. Actual: {finance_lease_proportion:,.2f}"
    else:
       covenant_financelease_concentration = f"NO BREACH: Finance-Lease proportion Proportion {finance_lease_proportion:,.2f}%"


    ##### New Features for Revenues:
    # Calculate Remaining Lease Term (Days) using the vectorized operation
    
    df_portfolio['Remaining Lease Term (Days)'] = (df_portfolio['End Contract Date'] - closing_date).dt.days

    # Calculate Age at Closing Date and Age at End of Contract

    df_portfolio['Age at End of Contract'] = (df_portfolio['Age at Closing Date'] + df_portfolio['Remaining Lease Term (Days)']) / 365


    # Calculate remaining years, annual revenue, and remaining life revenues
    df_portfolio['Lifecycle Remaining Years'] = 15 - df_portfolio['Age at Closing Date']
    df_portfolio['Annual Revenue'] = df_portfolio['Per Diem (Unit)'] * 365


    #### Output
    output = {"Covenants":{'4.a) Manufactured by an Acceptable Manufacturer': covenant_manufacturer,
                           '4.b) NBV Weighted Average Age (9 years max)': covenant_weight_avg_age,
                            '4.c) Avg. Lease Term of Post-2019 Equipment (greater than 5 years)' : covenant_avg_lease,
                            '4.d) Total Purchase Price by CEU (Under 2,900 USD)': covenant_nbv_ceu,
                            '5.19) Concentration Limits': dict_concentration_breach,
                            'Advance Rate Checking (Check)': covenant_advance_rate,
                            '5.13) OFF Lease Fleet NBV concentration (20% max)' : covenant_offlease_concentration,
                            '5.17) Finance Lease Fleet NBV concentration (Under 30%)' : covenant_financelease_concentration},
            "Portfolio":df_portfolio}
    
    return output 

# FUNCTION 2 : Function to export non leased units on the portfolio

def off_lease_units(path_portfolio, export_path):
    # Read the portfolio Excel file into a DataFrame
    df_portfolio = pd.read_excel(path_portfolio)

    rows = len(df_portfolio)

    # Calculate the proportion of leased equipment
    leased = len(df_portfolio[df_portfolio["Current Status"] == "On lease"])
    equipment_leased = leased / rows
    equipment_not_leased = 1 - equipment_leased

    # Create a DataFrame with only non-leased equipment
    non_leased_df = df_portfolio[df_portfolio["Current Status"] == "Off Lease"]

    # Calculate the total NBV of non-leased equipment
    total_non_leased_nbv = non_leased_df["Purchase Price"].sum()

    # Calculate the total NBV of all equipment
    total_nbv = df_portfolio["Purchase Price"].sum()

    # Calculate the proportion of NBV of non-leased equipment to the total NBV
    non_leased_nbv_proportion = total_non_leased_nbv / total_nbv

    # Rest of your code remains the same...
    
    output = {
        "Speculative NBV": total_non_leased_nbv,
        "Speculative NBV Allocation within the Portfolio": non_leased_nbv_proportion
    }

    return output

# FUNCTION 3 :  Function for debt calculation
def debt_payment_and_interest(
                              path_df,
                              NUM_PAYMENTS,
                              REPAYMENT_RATE = 0.015,
                              MARGIN = 0.0235, #2.35 percent per annum 
                              ADJUSTMENT = 0.0026161,
                              DAYS = 90/365,
                             ):
    """
    This function calculates the repayment instalment and interest payment in function of the evolving debt

    Parameters:
    initial_debt (float): This is the debt amount after the drawdown.
    repayment_amount (float): This is the debt amount multiplied by the repayment percentage.
    num_payments (float): This represents the number of periods in which we will be paying off the debt and interest.
    SOFR (float): Secured Overnight Financing Rate, which is used as the floating variable for interest calculation.
    DAYS (int): The number of days in a trimester, typically 90 days.

    The function also uses the following global constants:
    MARGIN (float): The margin value used for interest calculation.
    ADJUSTMENT (float): The adjustment value used for interest calculation.

    Returns:
    The function returns the remaining debt (float) and the total interest paid over the selected number of periods (float).
    """

    # Import Data
    # Data Frames
    df_portfolio = pd.read_excel(path_df,
                                 sheet_name='Planned Portfolio')
    df_debt = pd.read_excel(path_df,
                            sheet_name='Debt')
    df_SOFR = pd.read_excel(path_df.replace('Data_Set_Closing.xlsx','SOFR.xlsx'),
                            sheet_name='Results')

    # To modify
    SOFR = 0.0525

    initial_debt = df_portfolio['Purchase Price'].sum()
    repayment_amount = initial_debt * REPAYMENT_RATE
    new_debt = initial_debt

    total_interest = 0
    for _ in range(NUM_PAYMENTS):
        interest = new_debt * ((MARGIN/365 + SOFR + ADJUSTMENT) * DAYS)
        total_interest += interest
        new_debt = new_debt - repayment_amount
        new_debt = max(new_debt, 0)  # Ensure the debt doesn't become negative

    return {'initial_debt':initial_debt,
            'new_debt':new_debt, 
            'total_interest_paid':total_interest}



# FUNCTION 4 : Function to calculate the Cap and floor rates and payments
def calculate_hedge_payment(
                            path_df,
                            NOTIONAL,
                            NUM_PAYMENTS,
                            FLOOR = 0.0175, 
                            CAP = 0.03,
                            RATE_DAY_COUNT_FRACTION = 90/360.0
                            ):
    """
    Parameters:

    path_df: A file path to the 'Data_Set_Closing.xlsx' Excel file.
    NOTIONAL (float): Represents the notional amount for the Hedge.
    NUM_PAYMENTS (integer): Indicated the number of payments in the hedge.
    FLOOR (float): (default: 0.0175) is the lower boundary or floor rate for the SOFR.
    CAP (float): (default: 0.03) is the upper boundary or cap rate for the SOFR.
    RATE_DAY_COUNT_FRACTION: A fraction representing the portion of the year for which the rate is applicable.
    The default value is 90/360.0, suggesting a quarterly rate.

    Overview:

    The function calculates the payment that needs to be made for the hedge based on the SOFR which is read from an
    Excel file named 'SOFR.xlsx'. The function simulates future SOFR values using Monte Carlo methods and then
    determines the discounted payoff based on these simulations, taking into account the cap and floor rates.

    Details:

    The function reads the 'SOFR.xlsx' Excel file and retrieves the SOFR data.
    It sorts the SOFR data by the 'Effective Date' in descending order and converts the rate percentages from whole
    numbers to decimals.
    Initial parameters for the GBM (Geometric Brownian Motion) such as the most recent SOFR, mean and standard deviation
    of the SOFR series, and time intervals dt are determined.
    The function then simulates SOFR rates at each quarter (or as specified by NUM_PAYMENTS) using Monte Carlo.
    The simulation is repeated 1000 times, and the average value for each payment period is calculated.
    Using the simulated SOFR series, the function calculates the discounted payoff of the hedge. For each period:
    If the SOFR is above the CAP, the payoff is based on the difference between the SOFR and the CAP.
    If the SOFR is below the FLOOR, the payoff is based on the difference between the FLOOR and the SOFR.
    If the SOFR lies between the CAP and the FLOOR, there's no payoff.
    The calculated hedge payment (payoff) is returned in dictionary format with the key 'Hedge'.

    Note: This function assumes a hedging strategy based on the SOFR and calculates the required hedge payment based on
    a combination of current and simulated future rates. The simulated future rates are subject to stochastic processes,
    and the Monte Carlo method is used to average out the simulations. The final payment takes into account caps and
    floors, ensuring that the payment lies within predefined boundaries.
    """

    df_SOFR = pd.read_excel(path_df.replace('Data_Set_Closing.xlsx','SOFR.xlsx'),
                            sheet_name='SOFR')
    df_SOFR.fillna(method='ffill', inplace=True)
    
    df_SOFR.sort_values(by='observation_date', ascending=False, inplace=True)
    df_SOFR.reset_index(drop=True, inplace=True)
    df_SOFR['SOFR'] = df_SOFR['SOFR']/100

    # Get the las available SOFR and the parameters for the GBM
    SOFR_0 = df_SOFR['SOFR'][0]
    mean_SOFR = np.mean(df_SOFR['SOFR'])
    sd_SOFR = np.std(df_SOFR['SOFR'])
    dt = 1/NUM_PAYMENTS  # The rates are already in quarterly
    n = NUM_PAYMENTS

    # np.random.seed(123)
    # This keeps the same random generator to obtain the same random numbers,
    # the values then will depend only on the SOFR series given

    # Simulate the SOFR at each Q (NUM_PAYMENTS) Using Monte Carlo

    sofr_q_series = 0
    for i in range(1000):
        Wt = np.random.normal(0, np.sqrt(dt), size=(n))
        SOFR_Q1 = 0
        SOFR_Q1 += SOFR_0 * np.exp((mean_SOFR - (sd_SOFR**2)/2)*dt + sd_SOFR*Wt[0])
        SOFR_series = [SOFR_Q1]
        for i in range(n-1):
            SOFR_series.append(SOFR_series[i] * np.exp((mean_SOFR - (sd_SOFR**2)/2)*dt + sd_SOFR*Wt[i+1]))

        sofr_q_series += np.array(SOFR_series)
    
    sofr_q_series = sofr_q_series / 1000
        
    # Calculate the discounted Payoff
    payoff_discounted = 0
    for p, SOFR_Q in enumerate(sofr_q_series):
        if p == 0:
            if SOFR_Q > CAP:
                payoff_discounted += (SOFR_Q - CAP/100) * NOTIONAL * RATE_DAY_COUNT_FRACTION
            elif SOFR_Q < FLOOR:
                payoff_discounted += (FLOOR/100 - SOFR_Q) * NOTIONAL * RATE_DAY_COUNT_FRACTION
            else:
                payoff_discounted += 0
        else:
            if SOFR_Q > CAP:
                payoff_discounted += (SOFR_Q - CAP/100) * NOTIONAL * RATE_DAY_COUNT_FRACTION * 1/((1 + SOFR_0)**(p))
            elif SOFR_Q < FLOOR:
                payoff_discounted += (FLOOR/100 - SOFR_Q) * NOTIONAL * RATE_DAY_COUNT_FRACTION * 1/((1 + SOFR_0)**(p))
            else:
                payoff_discounted += 0

    return {'Hedge': payoff_discounted}



# FUNCTION 5: CASHFLOW

# Define your container_mapping dictionary
def cashflow_calculation(path_portfolio,
                         insurance_fees,
                         agency_fees,
                         handling_fees,
                         bad_debt,
                         NOTIONAL,
                         NUM_PAYMENTS,
                         discount_rate,
                         rv_ev,
                         pd_ev):
     
    df_portfolio = pd.read_excel(path_portfolio, sheet_name='Planned Portfolio')

    container_mapping = {
        "20'DC": 1000 * (1 + rv_ev),
        "40'DC": 1200 * (1 + rv_ev),
        "40'HC": 1400 * (1 + rv_ev)
    }

    # New column RV
    df_portfolio['RV'] = df_portfolio['Type'].apply(lambda x: container_mapping.get(x, 0))

    # Convert to date time
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])
    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])

    # Remaining contract days
    df_portfolio['Remaining Contract (days)'] = (df_portfolio['End Contract Date'] - df_portfolio['Closing Date']).dt.days
    df_portfolio['Contract Remaining Quarters'] = df_portfolio['Remaining Contract (days)'] / 90

    # Remaining economic life (only used for the Residual Value)
    df_portfolio['15 Years Date'] = df_portfolio['Manufacturing Date'] + pd.DateOffset(years=15)
    df_portfolio['Lifecycle Remaining Days'] = (df_portfolio['15 Years Date']  - df_portfolio['Closing Date']).dt.days
    df_portfolio['Lifecycle Remaining Quarters'] = df_portfolio['Lifecycle Remaining Days'] / 90

    # Economic life second contract
    df_portfolio['Remaining Days SC'] = (df_portfolio['15 Years Date'] - df_portfolio['End Contract Date']).dt.days
    df_portfolio['Remaining Days SC'] = [x if x > 0.0 else 0.0 for x in df_portfolio['Remaining Days SC']]
    df_portfolio['Remaining Quarters SC'] = df_portfolio['Remaining Days SC'] / 90

    # Create new columns for OPEX
    df_portfolio['Per Diem Cost Multiplier'] = insurance_fees + agency_fees + bad_debt + handling_fees
    df_portfolio['Total OPEX'] = df_portfolio['Per Diem (Unit)'] * df_portfolio['Per Diem Cost Multiplier']
    df_portfolio['Daily Cash Flow'] = df_portfolio['Per Diem (Unit)'] - df_portfolio['Total OPEX']
    df_portfolio['Daily Cash Flow SC'] = df_portfolio['Per Diem (Unit)']*(1+pd_ev) - df_portfolio['Total OPEX']

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

    quarters_rev = np.zeros(15*4)
    for g in groups:
        for row in df_grouped.get_group(g).itertuples():
            # First Contract:
            array_values = np.full(int(row[3]), row[8]*90)
            # Add RV first contract and remainder of last Quarter
            rv_rem = row[1] + (row[3] - int(row[3]))*90*row[8]*((1+discount_rate)**(1-row[3] - int(row[3])))
            array_values = np.append(array_values, rv_rem)
            # Second contract:
            array_values = np.append(array_values, np.full(int(row[7]), row[9]*90))
            # Add RV second contract and remainder of last Quarter
            if row[7] == 0:
                rv_sc = 0
            elif row[7] != 0:
                rv_sc = row[1]
            rem = (row[7] - int(row[7]))*90*row[9]*(1+discount_rate)**(1 - (row[7] - int(row[7])))
            array_values = np.append(array_values, rv_sc + rem)

            array_values.resize(15*4, refcheck=False)

            quarters_rev = quarters_rev + array_values

    NPV = np.sum([x*1/(1+discount_rate)**(i+1) for i, x in enumerate(quarters_rev)]) + calculate_hedge_payment(path_portfolio,
                                                                                                               NOTIONAL,
                                                                                                               NUM_PAYMENTS,
                                                                                                               FLOOR = 0.0175, 
                                                                                                               CAP = 0.03,
                                                                                                               RATE_DAY_COUNT_FRACTION = 90/360.0)['Hedge']
    ROI = ((NPV/df_portfolio['Purchase Price'].sum()) - 1)

    return {'ROI': ROI,
            'NPV': NPV
            }

# Function 6: CASH FLOW ONE CONTRACT

def cash_flow(path_portfolio,
                    insurance_fees,
                    agency_fees,
                    handling_fees,
                    bad_debt,
                    managment_fee,
                    sell_fee,
                    rv_ev,
                    euribor_year,
                    margin
                    ):
    
    # Load Data Frame with portfolio data
    df_portfolio = pd.read_excel(path_portfolio, sheet_name='Planned Portfolio')

    ### NBV AT END OF CONTRACT ###

    # Establish RV for units, it's for calculate the portfolio value (NBV)
    container_mapping = {
        "20'DC": 1100 * (1 + rv_ev),
        "40'DC": 1320 * (1 + rv_ev),
        "40'HC": 1540 * (1 + rv_ev)
    }

    df_portfolio['RV'] = df_portfolio['Type'].apply(lambda x: container_mapping.get(x, 0))

    r_annual = euribor_year + margin
    wacc = (1 + r_annual)**(1/365) - 1
    wacc_year = (euribor_year + margin) * 100

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
    operation_period = (end_date - start_date).days + 1
    operation_period_years = ((end_date - start_date).days + 1)/365

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

    # RATES: NPV (USD), ROI (%), IRR (%)
    portfolio_npv = df_revenues['NPV Leasing Revenues'].sum()
    portfolio_margin = df_revenues['Net Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()
    portfolio_margin_npv = df_revenues['NPV Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()
    portfolio_roi = (portfolio_margin / df_portfolio['Purchase Price'].sum()) * 100
    portfolio_npv_roi = ((df_revenues['NPV Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()) / df_portfolio['Purchase Price'].sum()) * 100
    portfolio_annual_roi = portfolio_roi / operation_period_years
    portfolio_annual_roi_npv = portfolio_annual_roi / operation_period_years


    # Export to Excel
    df_revenues.to_excel('/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/testdcf.xlsx', index=False)


    return {'Operation NPV': portfolio_npv,
            'Operation NPV Profit': portfolio_margin_npv,
            'Portfolio ROI (NPV Leasing Revenues)': portfolio_npv_roi,
            'Discount Rate' : wacc_year,
            'Operation Period (Days)': operation_period,
            'Operation Period (Years)': operation_period_years
            }

# Function 7: CASH FLOW ONE CONTRACT

def cash_flow_table(path_portfolio,
                    insurance_fees,
                    agency_fees,
                    handling_fees,
                    bad_debt,
                    managment_fee,
                    sell_fee,
                    rv_ev,
                    euribor_year,
                    margin
                    ):
    
    # Load Data Frame with portfolio data
    df_portfolio = pd.read_excel(path_portfolio, sheet_name='Planned Portfolio')

    ### NBV AT END OF CONTRACT ###

    # Establish RV for units, it's for calculate the portfolio value (NBV)
    container_mapping = {
        "20'DC": 1100 * (1 + rv_ev),
        "40'DC": 1320 * (1 + rv_ev),
        "40'HC": 1540 * (1 + rv_ev)
    }

    df_portfolio['RV'] = df_portfolio['Type'].apply(lambda x: container_mapping.get(x, 0))

    r_annual = euribor_year + margin
    wacc = (1 + r_annual)**(1/365) - 1
    wacc_year = (euribor_year + margin) * 100

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
    operation_period = (end_date - start_date).days + 1
    operation_period_years = ((end_date - start_date).days + 1)/365

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

    # RATES: NPV (USD), ROI (%), IRR (%)
    portfolio_npv = df_revenues['NPV Leasing Revenues'].sum()
    portfolio_margin = df_revenues['Net Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()
    portfolio_margin_npv = df_revenues['NPV Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()
    portfolio_roi = (portfolio_margin / df_portfolio['Purchase Price'].sum()) * 100
    portfolio_npv_roi = ((df_revenues['NPV Leasing Revenues'].sum() - df_portfolio['Purchase Price'].sum()) / df_portfolio['Purchase Price'].sum()) * 100
    portfolio_annual_roi = portfolio_roi / operation_period_years
    portfolio_annual_roi_npv = portfolio_annual_roi / operation_period_years


    # Export to Excel
    df_revenues.to_excel('/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/testdcf.xlsx', index=False)


    return {'Operation NPV': f'{portfolio_npv:,.2f} USD',
            'Operation NPV Profit': f'{portfolio_margin_npv:,.2f} USD',
            'Portfolio ROI (NPV Leasing Revenues)': f'{portfolio_npv_roi:,.2f} %',
            'Discount Rate' : f'{wacc_year:,.2f} %',
            'Operation Period (Days)': operation_period,
            'Operation Period (Years)': operation_period_years}