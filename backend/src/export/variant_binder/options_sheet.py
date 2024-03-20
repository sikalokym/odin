import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Alignment, Side

from openpyxl.utils import get_column_letter
from src.database.db_operations import DBOperations
from src.utils.db_utils import filter_df_by_timestamp


#General formating of border lines & cell colours in excel spreadsheet
all_border = Border(top=Side(style='thin', color='000000'),
                    bottom=Side(style='thin', color='000000'),
                    left=Side(style='thin', color='000000'),
                    right=Side(style='thin', color='000000'))

white_border = Border(right=Side(style='thin', color="FFFFFF"))
fill = PatternFill(start_color='000080', end_color='000080', fill_type='solid')

def get_sheet(ws, sales_versions, title, time):
    """
    Fetches options data and inserts it into the specified worksheet.

    Args:
        ws (Worksheet): The worksheet to insert the data into.
        sales_versions (DataFrame): The sales versions to fetch options data for.
        title (str): The title of the sheet.

    Returns:
        None
    """

    df_res = fetch_options_data(sales_versions, time)

    # Calculate the number of empty rows to append
    num_empty_rows = 2 - len(ws['A'])

    # Append empty rows
    for _ in range(num_empty_rows):
        ws.append([])

    # insert data into the sheet ab row 3
    for _, row in df_res.iterrows():
        ws.append([row['Code'], row['CustomName'], row['Price']] + [row[sv] for sv in sales_versions['SalesVersion']])

    prepare_sheet(ws, sales_versions.SalesVersionName, title)

def prepare_sheet(ws, sales_versions, title):
    max_r_pre = ws.max_row 

    # Format cells according to templates
    for row in range(max_r_pre, 3, -1):  # Beginne von unten, um die Position der Zeilen nicht zu verändern
        ws.insert_rows(row)

    row = 3
    while row <= max_r_pre:
    # Test if cell in column C has content
        if ws.cell(row=row, column=3).value:
        # Split up price data in column C
            prices = ws.cell(row=row, column=3).value.split('/')
        
        # Den zweiten Preis in die nächste leere Zeile verschieben
            if len(prices) > 1:
                next_empty_row = row + 1
                while ws.cell(row=next_empty_row, column=3).value:
                    next_empty_row += 1
                ws.cell(row=next_empty_row, column=3).value = float(prices[1])
                ws.cell(row=row, column=3).value = float(prices[0])
                max_r_pre += 1  # Eine zusätzliche Zeile wurde hinzugefügt, also erhöhe max_row
            row += 2  # Überspringe die nächste Zeile, da sie bereits eingefügt wurde
        else:
            row += 1

    # Finding of the last columns and rows with content for border lines
    max_c = ws.max_column
    max_r = ws.max_row 

    for row in range(3, max_r + 1, 2):
        ws.merge_cells(start_row=row, end_row=row + 1, start_column=1, end_column=1)  # Mergen von A-Zellen
        ws.merge_cells(start_row=row, end_row=row + 1, start_column=2, end_column=2)  # Mergen von B-Zellen
    for col in range(4, max_c + 1):
        for row in range(3, max_r + 1, 2):
            ws.merge_cells(start_row=row, end_row=row + 1, start_column=col, end_column=col)

    # Content of Row 1 & 2
    ws.merge_cells('A1:B1')
    ws['A1'] = f'{title} - Optionen'
    ws['C1'] = 'EUR inkl. 19 % MwSt.\n EUR ohne MwSt.'
    for idx, value in enumerate(sales_versions, start=4):
        ws.cell(row=1, column=idx, value=value)
    ws['A2'] = 'Code (ab Werk)\n + VCG Paket'
    ws['B2'] = 'Description'

    #Definition of column widths & row heights
    ws.column_dimensions['A'].width = 11
    ws.column_dimensions['B'].width = 65
    for col in range(3, max_c + 1):
        ws.column_dimensions[get_column_letter(col)].width = 25

    ws.row_dimensions[1].height = 45
    ws.row_dimensions[2].height = 35

    # Formatting of first row
    ws['A1'].font = Font(name='Arial', size=16, bold=True, color="FFFFFF")
    ws['A1'].alignment = Alignment(horizontal='left', vertical='center')

    for col in range(3, 20):
        cell = ws.cell(row=1, column=col)
        cell.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center', vertical='center',wrap_text=True)

    for col in range(1,max_c+1):
        cell = ws.cell(row=1, column=col)
        cell.fill = fill

    # Formatting of second row
    ws['A2'].alignment = Alignment(horizontal='center', vertical='center',wrap_text=True)
    ws['A2'].font = Font(size=10, bold=True)
    ws['B2'].alignment = Alignment(horizontal='center', vertical='center')
    ws['B2'].font = Font(size=10, bold=True)

    # Formatting of first row border lines
    for col in range(1, max_c):
        cell = ws.cell(row=1, column=col)
        cell.border = white_border

    # Setting of border lines context sensitive to last cells with content
    content_area = ws.iter_cols(min_row=3, max_row=max_r, min_col=1, max_col=max_c)
    for row in content_area:
        for cell in row:
            cell.border = all_border

    # Setting of border lines context sensitive around data
    for col in range(1, max_c + 1):
        cell = ws.cell(row=3, column=col)
        cell.border = Border(top=Side(style='medium'),
                            right=Side(style='thin'))

    for row in range(3, max_r + 1):
        cell = ws.cell(row=row, column=max_c)
        cell.border = Border(right=Side(style='medium'),
                            bottom=Side(style='thin'))

    for col in range(1, max_c + 1):
        cell = ws.cell(row=max_r, column=col)
        cell.border = Border(bottom=Side(style='medium'),
                            left=Side(style='thin'))

    top_right_cell = ws.cell(row=3, column=max_c)
    bottom_right_cell = ws.cell(row=max_r, column=max_c)

    top_right_cell.border = Border(right=Side(style='medium'),
                                        bottom=Side(style='thin'),
                                        top=Side(style='medium'),
                                        left=Side(style='thin'))

    bottom_right_cell.border = Border(right=Side(style='medium'),
                                        bottom=Side(style='medium'),
                                        top=Side(style='thin'),
                                        left=Side(style='thin'))

    # Formatting of data output format in Column C as EUR
    for row in range(3, max_r + 1):
        cell = ws.cell(row=row, column=3)
        cell.number_format = '€ #,##0.00'

    # Formatting of alignment of content cells
    for row in range(3, max_r + 1):
        for col in range(3, max_c + 1):
            cell = ws.cell(row=row, column=col)
            cell.alignment = Alignment(horizontal='center', vertical='center')

    for row in range(3, max_r + 1):
        cell = ws.cell(row=row, column=1)
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Formatting of "Pack Only" options
    for row in range(3, max_r + 1):  
        if ws.cell(row=row, column=3).value == "Pack Only":
            for col in range(1, max_c + 1):
                ws.cell(row=row, column=col).font = Font(color="A6A6A6")

    # Formatting of gap to extra section
    ws.column_dimensions[get_column_letter(max_c + 1)].width = 1

    # Formatting of extra section
    cat_col = max_c + 2  # Two columns after max_c
    ws.cell(row=1, column=cat_col).value = "Kategorie"

    ws.column_dimensions[get_column_letter(cat_col)].width = 25
    
    cat_cell = ws.cell(row=1, column=cat_col)
    cat_cell.font = Font(name='Arial', size=10, bold=True, color="FFFFFF")
    cat_cell.alignment = Alignment(horizontal='center', vertical='center')
    cat_cell.fill = fill

    for row in range(3, max_r + 1, 2):
        ws.merge_cells(start_row=row, end_row=row + 1, start_column=cat_col, end_column=cat_col)

    for row in range(3, max_r + 1):
        cell = ws.cell(row=row, column=cat_col)
        cell.border = Border(bottom=Side(style='thin'),
                            left=Side(style='thin'),
                            top=Side(style='thin'),
                            right=Side(style='thin'))
        
def fetch_options_data(sales_versions, time):
    df_pno_option_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'OPT_Custom'), columns=['RelationID', 'Price', 'PriceBeforeTax', 'CustomName'])
    df_pno_options = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'OPT'), columns=['ID', 'PNOID', 'Code', 'RuleName', 'StartDate', 'EndDate'])
    df_pno_options = filter_df_by_timestamp(df_pno_options, time)
    df_pno_options.drop(columns=['StartDate', 'EndDate'], inplace=True)
    
    sales_versions.rename(columns={'ID': 'TmpCode'}, inplace=True)
    df_pno_options = df_pno_options.merge(sales_versions[['TmpCode', 'SalesVersion', 'SalesVersionName']], left_on='PNOID', right_on='TmpCode', how='left')
    df_pno_options.drop(columns='TmpCode', inplace=True)
    df_pno_options_with_sv = df_pno_options[df_pno_options['SalesVersion'].notna()]
    # Replace ID with Price from df_pno_option_price
    df_pno_options_with_price = df_pno_options_with_sv.merge(df_pno_option_price, left_on='ID', right_on='RelationID', how='left')

    # Concatenate Price and PriceBeforeTax
    df_pno_options_with_price['Price'] = df_pno_options_with_price.apply(lambda x: f"{x['Price']}/{x['PriceBeforeTax']}" if x['RuleName'] != 'P' else 'Pack Only', axis=1)
    
    # Create the pivot table
    pivot_df = df_pno_options_with_price.pivot_table(index=['Code', 'Price'], columns='SalesVersion', values='RuleName', aggfunc='first')

    # Drop the now unneeded columns and duplicates
    df_pno_options_with_price.drop(['ID', 'PNOID', 'RelationID', 'RuleName', 'SalesVersion', 'SalesVersionName', 'PriceBeforeTax'], axis=1, inplace=True)
    df_pno_options_with_price.drop_duplicates(inplace=True)

    # Join the pivoted DataFrame with the original one. sort after code ascending
    df_result = df_pno_options_with_price.join(pivot_df, on=['Code', 'Price']).sort_values(by='Code')

    return df_result
