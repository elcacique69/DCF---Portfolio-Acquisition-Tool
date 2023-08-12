# Library
import pandas as pd


# Function for debt calculation
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

    return {'initial_debt': initial_debt,
            'new_debt': new_debt,
            'total_interest_paid': total_interest}



# Function to calculate the Cap and floor rates and payments
def calculate_hedge_payment(
                            path_df,
                            NOTIONAL,
                            NUM_PAYMENTS,
                            FLOOR = 0.0175, 
                            CAP = 0.03,
                            RATE_DAY_COUNT_FRACTION = 90/360.0
                            ):
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

    df_SOFR = pd.read_excel(path_df.replace('Data_Set_Closing.xlsx','SOFR.xlsx'),
                            sheet_name='Results')

    # To modify
    SOFR = 0.0525

    
    if SOFR > CAP:
        payoff = (SOFR - CAP) * NOTIONAL * RATE_DAY_COUNT_FRACTION
    elif SOFR < FLOOR:
        payoff = (FLOOR - SOFR) * NOTIONAL * RATE_DAY_COUNT_FRACTION
    else:
        payoff = 0

    return {'Hedge':payoff * NUM_PAYMENTS}



# Calculate

path_df = r'C:\Users\camil\Documents\GitHub\DCF---Portfolio-Acquisition-Tool\Data_Set_Closing.xlsx'

debt_and_interest = debt_payment_and_interest(path_df=path_df, NUM_PAYMENTS=20)
hedge_payment = calculate_hedge_payment(path_df=path_df, NOTIONAL=17000000, NUM_PAYMENTS=20)['Hedge']
payment_total = debt_and_interest['initial_debt'] - debt_and_interest['new_debt']
borrowing_expenses = (payment_total + debt_and_interest['total_interest_paid']) - hedge_payment

# Print Results
print(f"Current debt: {debt_and_interest['new_debt'] :,.2f} USD")
print(f"Total debt Payment: {payment_total:,.2f} USD")
print(f"Hedge receivable: {hedge_payment:,.2f} USD")
print(f"Paid interest: {debt_and_interest['total_interest_paid']:,.2f} USD")
print(f"Borrowing cost: {borrowing_expenses:,.2f} USD")
