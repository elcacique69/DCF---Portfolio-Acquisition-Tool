#%%
import os
import pathlib
import sys

library_tools_path = str(pathlib.PurePath(os.getcwd()))
sys.path.append(library_tools_path)

from Library_Portfolio_Tools import *


#%%
# Main
path_portfolio = "https://raw.githubusercontent.com/elcacique69/DCF---Portfolio-Acquisition-Tool/main/Data_Set_Closing.xlsx"
MIN_PRICE = 1500


#%%
results = bank_convenants(path_portfolio, MIN_PRICE)

#%%
df_portfolio = results[0]
df_expensive_containers = results[1]

print(results[2])
df_portfolio.head()
df_expensive_containers.head()
