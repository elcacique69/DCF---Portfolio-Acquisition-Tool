import pandas as pd
from tabulate import tabulate  # You'll need to install this library if not already done

def analyze_portfolio(path_portfolio, 
                      export_path
                      ):
    
    rows = len(path_portfolio)
    
    # Calculate the proportion of leased equipment
    leased = len(path_portfolio[path_portfolio["Current Status"] == "On lease"])
    equipment_leased = leased / rows
    equipment_not_leased = 1 - equipment_leased
    
    # Create a DataFrame with only non-leased equipment
    non_leased_df = path_portfolio[path_portfolio["Current Status"] == "Off Lease"]
    
    # Calculate the total NBV of non-leased equipment
    total_non_leased_nbv = non_leased_df["Purchase Price"].sum()
    
    # Calculate the total NBV of all equipment
    total_nbv = path_portfolio["Purchase Price"].sum()
    
    # Calculate the proportion of NBV of non-leased equipment to the total NBV
    non_leased_nbv_proportion = total_non_leased_nbv / total_nbv
    
    # Specify container types
    container_types = ["20'DC", "40'DC", "40'HC"]
    
    # Create a list to store container sum data
    container_sum_data = []
    for container_type in container_types:
        filtered_df = non_leased_df[non_leased_df['Type'] == container_type]
        sum_purchase_price = filtered_df['Purchase Price'].sum()
        container_sum_data.append({'Metric': f'{container_type} Purchase Price', 'Value': sum_purchase_price})
    
    # Create a DataFrame for container sum data
    container_sum_df = pd.DataFrame(container_sum_data)
    
    # Create a sample DataFrame for the Dashboard sheet
    dashboard_data = {
        'Metric': ['Total NBV of non-leased equipment', 'NBV proportion of non-leased equipment'],
        'Value': [total_non_leased_nbv, f"{non_leased_nbv_proportion * 100:.2f}%"]
    }
    dashboard_df = pd.DataFrame(dashboard_data)
    
    # Create an Excel writer object
    with pd.ExcelWriter(export_path, engine='xlsxwriter') as writer:
        # Write the DataFrames to the respective sheets
        non_leased_df.to_excel(writer, sheet_name='Non Leased Equipment', index=False)
        dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
        
        # Calculate the start row for the container sum DataFrame
        start_row = dashboard_df.shape[0] + 2
        container_sum_df.to_excel(writer, sheet_name='Dashboard', startrow=start_row, index=False)
        
    return{"Analysis results saved to Excel file"}

# Example usage
input_df = pd.read_excel("/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Data_Set_Closing.xlsx")  # Replace with your Excel data file
export_path = "/Users/carlosjosegonzalezacevedo/Documents/GitHub/DCF---Portfolio-Acquisition-Tool/Off_Lease_Units.xlsx"  # Replace with your desired output Excel file path

analyze_portfolio(input_df, export_path)
