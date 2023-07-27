# Library
import pandas as pd

# Data Frames
xl = pd.ExcelFile('/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx')
xls = pd.ExcelFile('/Users/carlosjosegonzalezacevedo/Documents/02_NEOMA/01_Thesis/Coding/01_DataFrames/SOFR.xlsx')

df = xls.parse('Results')
df_portfolio = xl.parse('Planned Portfolio')
df_debt = xl.parse('Debt')

# Constants
MARGIN = 0.0235 #2.35 percent per annum
ADJUSTMENT = 0.0026161
SOFR = 0.0525
REPAYMENT_RATE = 0.015
NOTIONAL = 17395585.46
NUM_PAYMENTS = 20 # 20 quarters meaning 5 years
CAP = 0.03
FLOOR = 0.0175
DAYS = 90 / 365

# Function for debt calculation
def debt_payment_and_interest(initial_debt, repayment_amount, num_payments, SOFR, DAYS):
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
    new_debt = initial_debt
    total_interest = 0
    for _ in range(num_payments):
        interest = new_debt * ((MARGIN / 365 + SOFR + ADJUSTMENT) * DAYS)
        total_interest += interest
        new_debt = new_debt - repayment_amount
        new_debt = max(new_debt, 0)  # Ensure the debt doesn't become negative
    return new_debt, total_interest

# Function to calculate the Cap and floor rates and payments
def calculate_hedge_payment(SOFR, CAP, FLOOR, NOTIONAL):
    """
    This function calculates either. If the bank (seller) pay the borrower (buyer), in a above cap rate or if
    the borrower (seller) pay the bank (borrower), in a below floor rate situation.

    Parameters:
    SOFR (float): Secured Overnight Financing Rate, which is used as the floating variable for cap or floor rate.
    CAP (float): option that provides the buyer with the right to receive payments if the SOFR exceeds the CAP.
    FLOOR (float): option that provides the buyer with the right to receive payments if the SOFR falls below the FLOOR.
    NOTIONAL(float): amount which is hedge in the contract between the bank and borrower.

    Returns:
    (float): The function returns the payment regarding if there is a CAP or FLOOR exit of the SWAP.
    """
    day_count_fraction = 90 / 360.0
    if SOFR > CAP:
        payment = (SOFR - CAP) * NOTIONAL * day_count_fraction
    elif SOFR < FLOOR:
        payment = (FLOOR - SOFR) * NOTIONAL * day_count_fraction
    else:
        payment = 0
    return payment

# Calculate
initial_debt = df_portfolio['Purchase Price'].sum()
repayment_of_loan = initial_debt * REPAYMENT_RATE

current_debt, total_interest = debt_payment_and_interest(initial_debt, repayment_of_loan, NUM_PAYMENTS, SOFR, DAYS)
hedge_payment = calculate_hedge_payment(SOFR, CAP, FLOOR, NOTIONAL) * NUM_PAYMENTS
payment_total = initial_debt - current_debt
total_expense = (payment_total + total_interest) - hedge_payment

# Print Results
print(f"Current debt: {current_debt:,.2f} USD")
print(f"Total debt Payment: {payment_total:,.2f} USD")
print(f"Hedge receivable: {hedge_payment:,.2f} USD")
print(f"Paid interest: {total_interest:,.2f} USD")
print(f"Borrowing cost: {total_expense:,.2f} USD")
