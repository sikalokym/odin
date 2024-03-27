from src.database.db_operations import DBOperations
from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter

from src.utils.db_utils import filter_df_by_timestamp, format_float_string
from openpyxl.styles.borders import Border
from openpyxl.styles import Side

all_border = Border(top=Side(style='thin', color='000000'),
                    bottom=Side(style='thin', color='000000'),
                    left=Side(style='thin', color='000000'),
                    right=Side(style='thin', color='000000'))

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
    df_colors = fetch_color_data(sales_versions, time)
    df_upholstery = fetch_upholstery_data(sales_versions, time)

    prepare_sheet(ws, sales_versions, title)

    # Write the data to the worksheet
    
    for _, row in df_upholstery.iterrows():
        prices = row['Price'].split('/')
        if len(prices) > 1:
            ws.append([row['Code'], row['CustomName'], prices[0]] + [row[sv] for sv in sales_versions['SalesVersion']])
            ws.cell(row=ws.max_row, column=3).alignment = Alignment(horizontal='center', vertical='bottom')
            ws.append(['', '', prices[1]] + [row[sv] for sv in sales_versions['SalesVersion']]) 
            ws.cell(row=ws.max_row, column=3).alignment = Alignment(horizontal='center', vertical='top')
            

        # format the cells
        for cell in ws[len(ws["A"])]:
            if row['Price'] =='Pack Only':
                cell.fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')
            cell.border = all_border
    
    ws.append([])
    ws.append([])
    curr_row = len(ws["A"]) + 2
    ws.merge_cells(f'A{curr_row}:B{curr_row}')
    ws[f'A{curr_row}'] = 'Außenfarben'
    ws[f'C{curr_row}'] = 'EUR inkl. 19 % MwSt.\n EUR ohne MwSt.'
    for idx, value in enumerate(sales_versions['SalesVersionName'], start=4):
        ws.cell(row=curr_row, column=idx, value=value)
        
    # Formatting of first row
    ws[f'A{curr_row}'].font = Font(name='Arial', size=16, bold=True, color="FFFFFF")
    ws[f'A{curr_row}'].alignment = Alignment(horizontal='left', vertical='center')
    
    for col in range(3, 20):
        cell = ws.cell(row=curr_row, column=col)
        cell.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center', vertical='center',wrap_text=True)
    max_c = ws.max_column
    for col in range(1,max_c+1):
        cell = ws.cell(row=curr_row, column=col)
        cell.fill = fill
        
    for _, row in df_colors.iterrows():
        ws.append([row['Code'], row['CustomName'], row['Price']] + [row[sv] for sv in sales_versions['SalesVersion']])
        # format the cells
        for cell in ws[len(ws["A"])]:
            cell.border = all_border

def prepare_sheet(ws, df_sales_versions, title):
    
    # Content of Row 1 & 2
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = ws['A2']
    ws.merge_cells('A1:B1')
    ws['A1'] = f'{title} - Polster & Farben'
    ws['C1'] = 'EUR inkl. 19 % MwSt.\n EUR ohne MwSt.'
    ws['A2'] = 'Code (ab Werk)\n + VCG Paket'
    ws['B2'] = 'Beschreibung'

    for idx, row in df_sales_versions.iterrows():
        ws.cell(row=1, column=idx+4, value=f'{row["SalesVersionName"]}\nSV {row["SalesVersion"]}')

    max_r_pre = ws.max_row 

    for row in range(max_r_pre, 3, -1):  # Beginne von unten, um die Position der Zeilen nicht zu verändern
        ws.insert_rows(row)

    row = 3
    while row <= max_r_pre:
    # Test if cell in column C has content
        if ws.cell(row=row, column=3).value:
        # Split up price data in column C
            prices = ws.cell(row=row, column=3).value.split('/')
        
        # Move second price into next row
            if len(prices) > 1:
                next_empty_row = row + 1
                while ws.cell(row=next_empty_row, column=3).value:
                    next_empty_row += 1
                ws.cell(row=next_empty_row, column=3).value = float(prices[1])
                ws.cell(row=row, column=3).value = float(prices[0])
                max_r_pre += 1  # One extra row has been added, so increase max_r
            row += 2  # Skip next row since it was added just now
        else:
            row += 1


    #Definition of column widths & row heights
    max_c = ws.max_column
    max_r = ws.max_row 

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
    

    # Formatting of content tables
    target_row = None
    for row in range(1, max_r):
        if ws.cell(row=row, column=1).value == "Außenfarben":
            target_row = row - 3  # Zwei Zeilen darüber
            break
    
    if target_row is not None:
        # Formatierung der Zellen im Bereich zwischen Zeile 3 und target_row
        for row in range(3, target_row + 1):
            for col in range(1, max_c + 1):
                cell = ws.cell(row=row, column=col)
                cell.border = Border(left=Side(style='thin'),
                                    right=Side(style='thin'),
                                    top=Side(style='thin'),
                                    bottom=Side(style='thin'))

        for row in range(3, target_row, 2):
            for col in range(1, 3):
                ws.merge_cells(start_row=row, start_column=col, end_row=row+1, end_column=col)
            for col in range(1, 2):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='right', vertical='center')
            for col in range(2, 3):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='left', vertical='center')
            for col in range(4, max_c + 1):
                ws.merge_cells(start_row=row, start_column=col, end_row=row+1, end_column=col)
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='center', vertical='center')
    
        # Formatting of second table
        for row in range(1, ws.max_row):
            if ws.cell(row=row, column=1).value == 'Außenfarben':
                for column in range(1, ws.max_column):
                    cell = ws.cell(row=row, column=column)
                    cell.font = Font(name='Arial', size=16, bold=True, color="FFFFFF")
                    cell.fill = fill
                break
    
        for row in range(target_row + 1 , max_r, 2):
            for col in range(1, 3):
                ws.merge_cells(start_row=row, start_column=col, end_row=row+1, end_column=col)
            for col in range(1, 2):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='right', vertical='center')
            for col in range(2, 3):
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='left', vertical='center')
            for col in range(4, max_c + 1):
                ws.merge_cells(start_row=row, start_column=col, end_row=row+1, end_column=col)
                cell = ws.cell(row=row, column=col)
                cell.alignment = Alignment(horizontal='center', vertical='center')

def fetch_color_data(sales_versions, time):
    df_pno_color = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'COL'), columns=['ID', 'PNOID', 'Code', 'RuleName', 'StartDate', 'EndDate'])
    df_pno_color = filter_df_by_timestamp(df_pno_color, time)
    df_pno_color_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'COL_Custom'), columns=['RelationID', 'Price', 'PriceBeforeTax', 'CustomName'])

    sales_versions.rename(columns={'ID': 'TmpCode'}, inplace=True)
    df_pno_color = df_pno_color.merge(sales_versions[['TmpCode', 'SalesVersion', 'SalesVersionName']], left_on='PNOID', right_on='TmpCode', how='left')
    df_pno_color.drop(columns='TmpCode', inplace=True)
    df_pno_color_with_sv = df_pno_color[df_pno_color['SalesVersion'].notna()]
    # Replace ID with Price from df_pno_color_price
    df_pno_color_with_price = df_pno_color_with_sv.merge(df_pno_color_price, left_on='ID', right_on='RelationID', how='left')

    # format prices to float using format_float_string
    df_pno_color_with_price['Price'] = df_pno_color_with_price['Price'].apply(format_float_string)
    df_pno_color_with_price['PriceBeforeTax'] = df_pno_color_with_price['PriceBeforeTax'].apply(format_float_string)

    # Concatenate Price and PriceBeforeTax
    df_pno_color_with_price['Price'] = df_pno_color_with_price.apply(lambda x: f"{x['Price']}/{x['PriceBeforeTax']}", axis=1)

    # Create the pivot table
    pivot_df = df_pno_color_with_price.pivot_table(index=['Code', 'Price'], columns='SalesVersion', values='RuleName', aggfunc='first')

    # Drop the now unneeded columns and duplicates
    df_pno_color_with_price.drop(['ID', 'PNOID', 'RelationID', 'RuleName', 'SalesVersion', 'SalesVersionName', 'PriceBeforeTax'], axis=1, inplace=True)
    df_pno_color_with_price.drop_duplicates(inplace=True)

    # Join the pivoted DataFrame with the original one. sort after code ascending
    df_result = df_pno_color_with_price.join(pivot_df, on=['Code', 'Price']).sort_values(by='Code')

    return df_result

def fetch_upholstery_data(sales_versions, time):
    df_pno_upholstery = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'UPH'), columns=['ID', 'PNOID', 'Code', 'RuleName', 'StartDate', 'EndDate'])
    df_pno_upholstery = filter_df_by_timestamp(df_pno_upholstery, time)
    df_pno_upholstery_price = DBOperations.instance.get_table_df(DBOperations.instance.config.get('RELATIONS', 'UPH_Custom'), columns=['RelationID', 'Price', 'PriceBeforeTax', 'CustomName'])

    sales_versions.rename(columns={'ID': 'TmpCode'}, inplace=True)
    df_pno_upholstery = df_pno_upholstery.merge(sales_versions[['TmpCode', 'SalesVersion', 'SalesVersionName']], left_on='PNOID', right_on='TmpCode', how='left')
    df_pno_upholstery.drop(columns='TmpCode', inplace=True)
    df_pno_upholstery_with_sv = df_pno_upholstery[df_pno_upholstery['SalesVersion'].notna()]
    # Replace ID with Price from df_pno_upholstery_price
    df_pno_upholstery_with_price = df_pno_upholstery_with_sv.merge(df_pno_upholstery_price, left_on='ID', right_on='RelationID', how='left')

    # format prices to float using format_float_string
    df_pno_upholstery_with_price['Price'] = df_pno_upholstery_with_price['Price'].apply(format_float_string)
    df_pno_upholstery_with_price['PriceBeforeTax'] = df_pno_upholstery_with_price['PriceBeforeTax'].apply(format_float_string)

    # Concatenate Price and PriceBeforeTax
    df_pno_upholstery_with_price['Price'] = df_pno_upholstery_with_price.apply(lambda x: f"{x['Price']}/{x['PriceBeforeTax']}", axis=1)

    # Create the pivot table
    pivot_df = df_pno_upholstery_with_price.pivot_table(index=['Code', 'Price'], columns='SalesVersion', values='RuleName', aggfunc='first')

    # Drop the now unneeded columns and duplicates
    df_pno_upholstery_with_price.drop(['ID', 'PNOID', 'RelationID', 'RuleName', 'SalesVersion', 'SalesVersionName', 'PriceBeforeTax'], axis=1, inplace=True)
    df_pno_upholstery_with_price.drop_duplicates(inplace=True)

    # Join the pivoted DataFrame with the original one. sort after code ascending
    df_result = df_pno_upholstery_with_price.join(pivot_df, on=['Code', 'Price']).sort_values(by='Code')

    return df_result
