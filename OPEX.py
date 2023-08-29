import pandas as pd
import pathlib
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate


library_tools_path = str(pathlib.PurePath(os.getcwd()))
sys.path.append(library_tools_path)

path_portfolio = library_tools_path + '/Data_Set_Closing.xlsx'
path_asset_register = library_tools_path + '/Data_Set_Closing.xlsx'
sheet_name = 'Updated Asset Register'
export_path = library_tools_path + '/Off_Lease_Units.xlsx'

import Library_Portfolio_Tools as lpt

closing_date_close = datetime(2023, 6, 12)

def portfolio_description(path_portfolio, path_asset_register, closing_date):
   
    # Read the portfolio Excel file into a DataFrame
    df_portfolio = pd.read_excel(path_portfolio)
    df_asset_register = pd.read_excel(path_asset_register, sheet_name=sheet_name)

    # Calculate the age for each container row
    df_portfolio['Age at Closing Date'] = (closing_date - df_portfolio['Manufacturing Date']).dt.days / 365

    # Calculate the weighted age using the "Age" and "Purchase Price" columns
    df_portfolio['Weighted Age (Years)'] = df_portfolio['Age at Closing Date'] * df_portfolio['Purchase Price'] / df_portfolio['Purchase Price'].sum()

    # Calculate the weighted average age
    weighted_average_age = df_portfolio['Weighted Age (Years)'].sum()

    # Group by Lessee and Type
    grouped = df_portfolio.groupby(['Lessee', 'Type'])

    # Short Description
    portfolio_purchase_price = df_portfolio['Purchase Price'].sum()  # Purchase Price
    portfolio_units = len(df_portfolio)

    results = []
    for group, group_df in grouped:
        purchase_price = group_df['Purchase Price'].sum()
        ceu = group_df['CEU'].sum()
        units = len(group_df)
        avg_age = group_df['Age at Closing Date'].mean()
        roi_annual = (group_df['Per Diem (Unit)'] * 365) / group_df['Purchase Price']
        
        result = {
            'Lessee': group[0],
            'Type': group[1],
            'Units': units,
            'CEU': ceu,
            'Average Age': avg_age,
            'Purchase Price': purchase_price,
            'ROI Annual': roi_annual.mean(),  # Taking the mean of the ROI values
        }
        results.append(result)

    description = {
        'Portfolio Price': portfolio_purchase_price,
        'Portfolio Units': portfolio_units
    }
    
    # Calcula el NBV total por arrendatario (Lessee)
    nbv_by_lessee = df_portfolio.groupby('Lessee')['Purchase Price'].sum()

    # Crea un gráfico de torta para la concentración del NBV por arrendatario
    plt.figure(figsize=(8, 8))
    plt.pie(nbv_by_lessee, labels=nbv_by_lessee.index, autopct='%1.1f%%', startangle=140)
    plt.title('Portfolio Lessee Distribution')
    plt.axis('equal')  # Hace que el gráfico de torta sea circular
    plt.savefig('nbv_concentration.png')  # Guarda el gráfico como imagen
    plt.close()  # Cierra la figura para liberar memoria

    # NBV by Lessee combined Portfolio
    nbv_lessee = df_asset_register.groupby('Lessee')['NBV'].sum()

    # Calcular el porcentaje de NBV para cada arrendatario
    total_nbv = nbv_lessee.sum()
    nbv_percentages = nbv_lessee / total_nbv * 100

    # Identificar las categorías con menos del 3% y agruparlas en "Others"
    threshold_percentage = 3
    nbv_lessee_others = nbv_lessee[nbv_percentages >= threshold_percentage]
    nbv_lessee_others['Others'] = nbv_lessee[nbv_percentages < threshold_percentage].sum()

    # Crea un gráfico de torta para la concentración del NBV por arrendatario en el Updated Asset Register con "Others"
    plt.figure(figsize=(8, 8))
    plt.pie(nbv_lessee_others, labels=nbv_lessee_others.index, autopct='%1.1f%%', startangle=140)
    plt.title('Updated Asset Register NBV Concentration')
    plt.axis('equal')  # Hace que el gráfico de torta sea circular
    plt.savefig('nbv_concentration_asset_register.png')  # Guarda el gráfico como imagen
    plt.close()  # Cierra la figura para liberar memoria


    
    return results, description, 'nbv_concentration.png', 'nbv_concentration_asset_register.png'

test_results, test_description, nbv_concentration_image, nbv_concentration_asset_register = portfolio_description(path_portfolio, path_asset_register, closing_date=closing_date_close)

print("Results Table:")
print(tabulate(test_results, headers="keys", tablefmt="pretty"))
print("\nDescription:")
print(tabulate([test_description], headers="keys", tablefmt="pretty"))
print("\nNBV Concentration Image:", nbv_concentration_image)
