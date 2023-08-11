import pandas as pd

def calculate_quarterly_revenues():
    """
    description
    """
    df_portfolio = pd.read_excel(
        '/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx',
        sheet_name= 'Planned Portfolio'
    )

    # Putting everything on date format

    df_portfolio['Closing Date'] = pd.to_datetime(df_portfolio['Closing Date'])
    df_portfolio['End Contract Date'] = pd.to_datetime(df_portfolio['End Contract Date'])

    # Constants

    quarter = 90  # days

    # New Columns:

    df_portfolio['Remaining Lease Term (Days)'] = \
        (df_portfolio['End Contract Date'] - df_portfolio['Closing Date']).dt.days

    df_portfolio['Quarterly Revenues'] = df_portfolio['Per Diem (Unit)'] * quarter

    df_portfolio['Contra']

    # Operations



    df['Total Revenue'] = df['Per Diem (Unit)'] * df['Contract Days']
    revenue_df = df[['Contract Number', 'Closing Date', 'Total Revenue', 'Contract Quarters']]
    revenue_df.set_index('Closing Date', inplace=True)
    quarterly_revenues = revenue_df.groupby('Contract Number').resample('Q').sum()

    return quarterly_revenues

# Ruta del archivo
file_path = '/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx'
sheet_name = 'Planned Portfolio'

# Ejemplo de uso
quarterly_revenues = calculate_quarterly_revenues()
print(quarterly_revenues)
