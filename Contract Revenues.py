import pandas as pd
import numpy as np

def calculate_quarterly_revenues(file_path, sheet_name):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    df['Closing Date'] = pd.to_datetime(df['Closing Date'])
    df['End Contract Date'] = pd.to_datetime(df['End Contract Date'])
    df['Contract Days'] = (df['End Contract Date'] - df['Closing Date']).dt.days

    # Manejar los casos en los que Contract Days pueda ser cero o NA
    df['Contract Quarters'] = np.where(
        df['Contract Days'] > 0,
        np.ceil(df['Contract Days'] / 90).astype(int),
        0 # Valor predeterminado si Contract Days es <= 0
    )

    df['Total Revenue'] = df['Per Diem (Unit)'] * df['Contract Days']
    revenue_df = df[['Contract Number', 'Closing Date', 'Total Revenue', 'Contract Quarters']]
    revenue_df.set_index('Closing Date', inplace=True)
    quarterly_revenues = revenue_df.groupby('Contract Number').resample('Q').sum()

    return quarterly_revenues

# Ruta del archivo
file_path = '/Users/carlosjosegonzalezacevedo/Downloads/Data_Set_Closing (3).xlsx'
sheet_name = 'Planned Portfolio'

# Ejemplo de uso
quarterly_revenues = calculate_quarterly_revenues(file_path, sheet_name)
print(quarterly_revenues)
