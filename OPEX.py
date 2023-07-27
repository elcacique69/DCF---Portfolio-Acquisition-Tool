import pandas as pd

# Read data from Excel file into a DataFrame
xl = pd.ExcelFile('/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx')
path_portfolio = xl.parse('Planned Portfolio')

# Calculate the total number of containers for each type
container_counts = path_portfolio['Type'].value_counts()

# Define the daily charges, cost percentages, and default annual costs
storage_daily_charge = {
    "20'DC": 0.55,
    "40'DC": 1.10,
    "40'HC": 1.10
}

public_liability_percentage = {
    "20'DC": 0.02,
    "40'DC": 0.02,
    "40'HC": 0.02
}

annual_cost_insurance_percentage = {
    "20'DC": 0.25,
    "40'DC": 0.25,
    "40'HC": 0.25
}

# Calculate the total storage cost for each container type
storage_cost = {container_type: container_counts.get(container_type, 0) * storage_daily_charge[container_type] * 365
                for container_type in storage_daily_charge}

# Calculate the public liability cost for each container type
public_liability_cost = {container_type: container_counts.get(container_type, 0) * public_liability_percentage[container_type] * path_portfolio['Purchase Price']
                         for container_type in public_liability_percentage}

# Calculate the annual insurance cost for each container type
annual_insurance_cost = {container_type: container_counts.get(container_type, 0) * annual_cost_insurance_percentage[container_type] * path_portfolio['Purchase Price']
                         for container_type in annual_cost_insurance_percentage}

# Calculate the sum of yearly expenses
total_yearly_expenses = sum(storage_cost.values()) + sum(public_liability_cost.values()) + sum(annual_insurance_cost.values())

# Print the total yearly expenses
print("Total Yearly Expenses: ", total_yearly_expenses)
