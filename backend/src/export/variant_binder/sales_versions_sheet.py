from openpyxl.styles import PatternFill, Border, Side, Alignment, Font
from openpyxl.utils import get_column_letter
from src.database.db_operations import DBOperations
from src.utils.db_utils import filter_df_by_timestamp
import pandas as pd

all_border = Border(top=Side(style='thin', color='000000'),
                    bottom=Side(style='thin', color='000000'),
                    left=Side(style='thin', color='000000'),
                    right=Side(style='thin', color='000000'))

fill = PatternFill(start_color='000080', end_color='000080', fill_type='solid')

def get_sheet(ws, sales_versions, title, country, time):
    """
    Fetches options data and inserts it into the specified worksheet.

    Args:
        ws (Worksheet): The worksheet to insert the data into.
        sales_versions (DataFrame): The sales versions to fetch options data for.
        title (str): The title of the sheet.

    Returns:
        None
    """
    df_sales_versions = fetch_sales_version_data(sales_versions, country, time)

    # Write the title
    ws['A1'] = title
    ws['A1'].font = Font(size=16, bold=True)
    ws.merge_cells('A1:F1')
    ws['A1'].alignment = Alignment(horizontal='center')
    ws.freeze_panes = ws['A2']

    ws.column_dimensions['A'].width = 11
    ws.column_dimensions['B'].width = 150

    ws.row_dimensions[1].height = 45
    ws.row_dimensions[2].height = 35

    # Formatting of first row
    ws['A1'].font = Font(name='Arial', size=16, bold=True, color="FFFFFF")
    ws['A1'].alignment = Alignment(horizontal='left', vertical='center')
    
    for col in range(1,2):
        cell = ws.cell(row=1, column=col)
        cell.fill = fill

    # Formatting of second row
    ws['A2'].alignment = Alignment(horizontal='center', vertical='center',wrap_text=True)
    ws['A2'].font = Font(size=10, bold=True)
    ws['B2'].alignment = Alignment(horizontal='center', vertical='center')
    ws['B2'].font = Font(size=10, bold=True)

    # Write the headers
    ws.append(['Feature Code (Reference)', 'Serienausstattung'])
    ws.append([])

    for (sv, svn), group in df_sales_versions.groupby(['SalesVersion', 'SalesVersionName']):
        group.drop(columns=['SalesVersion', 'SalesVersionName'], inplace=True)
        df_options = group.sort_values(by='CustomName', ascending=True)

        # Write the data to the worksheet
        ws.append([sv, svn])
        # format the row in gray
        for cell in ws[len(ws["A"])]:
            cell.fill = PatternFill(start_color='BFBFBF', end_color='BFBFBF', fill_type='solid')

        for _, row in df_options.iterrows():
            ws.append([row['Code'], row['CustomName']])
            
def fetch_sales_version_data(df_sales_versions, country, time):
    pno_ids = df_sales_versions.ID.unique().tolist()
    conditions = []
    if len(pno_ids) == 1:
        conditions.append(f"PNOID = '{pno_ids[0]}'")
    else:
        conditions.append(f"PNOID in {tuple(pno_ids)}")
    df_pno_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('AUTH', 'FEAT'), columns=['PNOID', 'Code', 'Reference', 'Options', 'CustomName'], conditions=conditions)
    df_features = DBOperations.instance.get_table_df(DBOperations.instance.config.get('TABLES', 'FEA'), columns=['Code', 'MarketText', 'StartDate', 'EndDate'], conditions=[f'CountryCode = {country}'])
    df_features = filter_df_by_timestamp(df_features, time)
    df_features.drop(columns=['StartDate', 'EndDate'], inplace=True)
    df_features.drop_duplicates(subset=['Code'], keep='first', inplace=True)

    sv_correct_order = df_sales_versions.SalesVersion.unique().tolist()

    df_pno_features_sv = df_pno_features.merge(df_sales_versions[['ID', 'SalesVersion', 'SalesVersionName']], left_on='PNOID', right_on='ID', how='inner')
    df_pno_features_sv['SalesVersion'] = pd.Categorical(df_pno_features_sv['SalesVersion'], sv_correct_order)
    df_pno_features_sv.sort_values(by='SalesVersion', inplace=True)
    df_pno_features_sv.drop_duplicates('Code', keep='first', inplace=True)

    df_merged = df_pno_features_sv.merge(df_features, on=['Code'], how='left')
    df_merged['CustomName'] = df_merged['CustomName'].combine_first(df_merged['MarketText'])
    df_merged.drop(columns=['MarketText', 'ID', 'PNOID'], inplace=True)

    # df_merged['Code'] = df_pno_features['Code'].apply(lambda x: f'{x}({df_pno_features["Reference"]})')
    return df_pno_features_sv
