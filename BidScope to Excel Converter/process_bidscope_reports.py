# Auto-install required packages
from pypdfium2_raw import FWL_VKEY_BROWSER_Search
from xlwings.constants import AutoFilterOperator


def ensure_package(pkg):
    try:
        __import__(pkg)
    except ImportError:
        import subprocess, sys
        print(f"{pkg} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print(f"{pkg} installed successfully.")

# List all required packages here
required_packages = [
    "pdfplumber",
    "pandas",
    "openpyxl",
    "xlwings"
]

for pkg in required_packages:
    ensure_package(pkg)

import os
import re
import pdfplumber
import xlwings as xw
import pandas as pd
import shutil
import openpyxl

INPUT_DIR = 'input'
OUTPUT_DIR = 'output'

def main():
    #Changes the path into wherever this script is running no matter where
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    ###1. CHOOSE YOUR REPORTS
    try:
        messy_bidder_file = os.path.join(INPUT_DIR, "ListofBidders.csv")
        messy_source_file = os.path.join(INPUT_DIR, "LOWSIXBIDDERSBYITEMS.csv")
        messy_budget_file = os.path.join(INPUT_DIR, "LowSixbyBudget.csv")
        bidtab_file_path = os.path.join(INPUT_DIR, "Bid Tab.pdf")

        # Template file
        beautiful_master_file = os.path.join(INPUT_DIR, "Beautiful Spreadsheet (DO NOT DELETE).xlsx")

        # Read data from the messy files first
        df_bidder = pd.read_csv(messy_bidder_file)
        df_source = pd.read_csv(messy_source_file)
        df_budget = pd.read_csv(messy_budget_file)



        ###2. DATA EXTRACTION
        # Extract respective columns from MB1
        df_bidders = df_bidder[[
            'detIMRANKing1',  # Bidder Ranking
            'detUUUCONTACTCOMPANY1'  # Contractor Name
        ]]

        # Copy from MB4 data from downloading the file from the Bid Report into a new dataframe
        df_raw_data = df_source[[
            'det1IMITEMNUMBERTXT1',  # Item Number
            'det1IMITEMUNITCODEPD1',  # Item Code
            'det1qty1',  # Item Quantity
            'det1Field1',  # Engineer's Estimate
            'det1Field2',  # Bidder 1
            'det1Field3',  # Bidder 2
            'det1Field4',  # Bidder 3
            'det1Field5',  # Bidder 4
            'det1Field6',  # Bidder 5
            'det1Field7',  # Bidder 6
            'det1IMITEMDESCRIPTIONTXT1'  # Item Description
        ]].reset_index(drop=True)

        ###3. TRANSFORM VIA DATA FILTERING
        # Create helper columns
        df_raw_data["helper_column_one"] = df_raw_data["det1qty1"]
        df_raw_data["helper_column_two"] = df_raw_data["det1Field1"]
        df_raw_data["helper_column_three"] = df_raw_data["det1Field2"]

        cols = ["helper_column_one", "helper_column_two", "helper_column_three"]

        df_raw_data[cols] = df_raw_data[cols].apply(lambda x: x.str.replace(',', '').astype(float))

        # For rows 0–1099 use helper columns to find % difference between Engineer's Estimate and Bidder 1
        df_raw_data.loc[:1099, "helper_result"] = ((df_raw_data["helper_column_two"] - df_raw_data[
        "helper_column_three"])) / (df_raw_data["helper_column_two"])

        # Do the same thing but with budget data in MB3
        df_raw_budget_data = df_budget[[
            'rfCrossTab1_TbxRowLabel1',
            'rfCrossTab1_TbxRow1'
        ]]
        # In MB1 Tell Python to only keep rows where the rank is exactly 1, 2, 3, 4, 5, or 6
        target_ranks = [1, 2, 3, 4, 5, 6]
        # Filter the dataframe
        df_bidders_filtered = df_bidders[df_bidders['detIMRANKing1'].isin(target_ranks)]

        # From MB3 Create a counter for each price within the same budget code group
        df_raw_budget_data['price_index'] = df_raw_budget_data.groupby('rfCrossTab1_TbxRowLabel1').cumcount() + 1
        # Pivot the raw_budget table from Long to Wide format
        df_wide = df_raw_budget_data.pivot(
            index='rfCrossTab1_TbxRowLabel1',
            columns='price_index',
            values='rfCrossTab1_TbxRow1'
        ).reset_index()
        # Clean up the MB3 column names so they internally read nicely as "Price_1", "Price_2", etc.
        df_wide.columns = ['rfCrossTab1_TbxRowLabel1'] + [f'Bidder_{col}' for col in df_wide.columns[1:]]

        # Filter for utilities from MB4, Filter for rows that contain 'JB' OR 'UTL' in the item number column
        df_utils = df_raw_data[df_raw_data['det1IMITEMNUMBERTXT1'].str.contains('JB|UTL', case=True, na=False)]

        ###4. LOAD BID TAB DATA
        with pdfplumber.open(bidtab_file_path) as pdf:
            text = pdf.pages[0].extract_text()


        # Regex function for splitting text in pdfplumber
        match = re.search(r"BID\s+TAB\s*\n\s*([A-Za-z0-9-]+(?:\s+\(REBID\d+\))?)\s+(.*)", text, re.IGNORECASE)

        if match:
            project_id = match.group(1).strip()  # Grabs project ID
            description = match.group(2).strip()  # Grabs descriptiion text
        else:
            project_id = "Unknown"
            description = None

        # Grabs everything after "Bid Date:" up to the end of that line
        bid_date_match = re.search(r"Bid Date:\s*(.*)", text, re.IGNORECASE)
        bid_date = bid_date_match.group(1).strip() if bid_date_match else None

        # Grabs everything after "EPIN:" up to the end of that line
        epin_match = re.search(r"EPIN:\s*(.*)", text, re.IGNORECASE)
        epin = epin_match.group(1).strip() if epin_match else None

        project_info_data = {
            "Project ID": [project_id],
            "EPIN": [epin],
            "Bid Date": [bid_date],
            "Description": [description]
        }

        # Convert it into a single-row DataFrame
        df_project_info = pd.DataFrame(project_info_data)

        ###5. DATA TRANSFER
        # Use ExcelWriter function to transfer data into Beautiful Spreadsheet respective tabs
        with pd.ExcelWriter(beautiful_master_file, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
            df_raw_data.to_excel(writer, sheet_name="RAW_DATA", index=False)
            # Write the budget data to a BUDGET_CODES tab
            df_wide.to_excel(writer, sheet_name="BUDGET_CODES", index=False)
            df_utils.to_excel(writer, sheet_name="UTILITIES_LIST", index=False)
            df_bidders_filtered.to_excel(writer, sheet_name="BIDDERS_NAME", index=False)
            df_project_info.to_excel(writer, sheet_name="PROJECT_INFO", index=False)

        ###6. Apply filter programattically in Excel
        # Open Excel silently in the background
        app = xw.App(visible=False)
        wb = xw.Book(
            os.path.join(INPUT_DIR, "Beautiful Spreadsheet (DO NOT DELETE).xlsx"))

        # Force Excel to calculate formulas and reapply the Table filters
        app.api.Calculate()
        # Dynamically loop through every single sheet
        for ws in wb.sheets:
            sheet_api = ws.api
            # Loop through every Excel Table (ListObject) on this specific sheet
            for table in sheet_api.ListObjects:
                try:
                    # Clear any stale filters on the table first to reset the state
                    if table.ShowAutoFilter:
                        table.AutoFilter.ShowAllData()
                    # Extract header names from the table to find the target column dynamically
                    headers = [cell.Value for cell in table.HeaderRowRange]
                    # If this is your specific Estimate tab, look for the "ESTIMATE" column
                    if "BC" in ws.name and "ESTIMATE" in headers:
                        col_index = headers.index("ESTIMATE") + 1

                        # Applies the filter (this hides zeroes; change to "<>" if you want to hide blanks instead)
                        table.Range.AutoFilter(Field=col_index, Criteria1="<>0")

                    # For all other tabs, default back to looking for "Quantity"
                    elif "Quantity" in headers:
                        col_index = headers.index("Quantity") + 1
                        table.Range.AutoFilter(Field=col_index, Criteria1="<>0")
                    elif "UTL" in ws.name.upper():
                        # and "Quantity" in headers:
                        col_index = headers.index("EE Price") + 1
                        table.Range.AutoFilter(Field=col_index,
                            Criteria1=">0",
                            Operator=AutoFilterOperator.xlOr,
                            Criteria2="<0")
                    else:
                        table.AutoFilter.ApplyFilter()
                except Exception:
                    pass
    except FileNotFoundError:
        exit("Error! Try checking your files and making sure you have the right ones or their names are correct.")

    ###7. SAVE AND CREATE A NEW COPY
    wb.save(
        os.path.join(INPUT_DIR, "Beautiful Spreadsheet (DO NOT DELETE).xlsx"))
    wb.close()
    app.quit()

    original_file = os.path.join(INPUT_DIR, "Beautiful Spreadsheet (DO NOT DELETE).xlsx")
    created_file = os.path.join(OUTPUT_DIR, "Beautiful Spreadsheet Filled.xlsx")

    shutil.copy2(original_file, created_file)

    ###8. Rename sheets in created_file using xlwings
    wb2 = xw.Book(created_file)
    sheet1 = wb2.sheets["SUMMARY"]
    sheet1.name = project_id + "_SUMMARY"
    sheet2 = wb2.sheets["MB4_CSV_6_BIDS_SS"]
    sheet2.name = project_id + "_MB4_CSV_6_BIDS_SS"
    sheet3 = wb2.sheets["LB_VS_EE"]
    sheet3.name = project_id + "_LB_VS_EE"
    sheet4 = wb2.sheets["2B_VS_LB"]
    sheet4.name = project_id + "_2B_VS_LB"
    sheet5 = wb2.sheets["BC"]
    sheet5.name = project_id + "_BC"
    sheet6 = wb2.sheets["UTL"]
    sheet6.name = project_id + "_UTL"

    ##Make helper tabs invisible
    wb2.sheets['RAW_DATA'].api.Visible = False
    wb2.sheets['BUDGET_CODES'].api.Visible = False
    wb2.sheets['UTILITIES_LIST'].api.Visible = False
    wb2.sheets['BIDDERS_NAME'].api.Visible = False
    wb2.sheets['PROJECT_INFO'].api.Visible = False

    wb2.save(os.path.join(OUTPUT_DIR, "Beautiful Spreadsheet Filled.xlsx"))

if __name__ == "__main__":
    main()

print("Data transfer successful! Open your beautiful Excel sheet to see the updates. :)")