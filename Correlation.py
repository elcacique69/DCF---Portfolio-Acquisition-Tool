# Library
import pandas as pd


df = \
    pd.read_excel('/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Coorelation.xlsx')

# Calcular la tasa de cambio del PD
df["PD Change"] = df["PD"].diff()

# Calcular la correlación entre el aumento del PD y las otras variables
correlation_with_pd_change = df[["PD Change",
                                 "Used Containers Price",
                                 "New Container Price",
                                 "Replacement",
                                 "Operating Ratio",
                                 "World GDP"
                                 ]].corr()

print(correlation_with_pd_change)
