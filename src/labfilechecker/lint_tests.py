import pandas as pd
from .lint_result import LintResult

def column_names(df, config):
    """Check if all column names are correct."""
    config_headers = set(v['Column_name'] for v in config.values())
    df_headers = set(df.columns)

    unknown_headers = config_headers - df_headers - set(['Row_Number'])
    missing_headers = df_headers - config_headers - set(['Row_Number'])

    passed = []
    warned = []
    failed = []
    if unknown_headers:
        for header in unknown_headers:
            warned.extend([
                LintResult(
                    row=None,
                    column=None,
                    value=header,
                    lint_test="column-names",
                    message=f"Column name {header} is not present in excel"
                )]
            )
    if missing_headers: 
        for header in missing_headers:
            warned.extend([
                LintResult(
                    row=None,
                    column=None,
                    value=header,
                    lint_test="column-names",
                    message=f"Column name {header}, is not defined in config update config"
                )]
            )
    if not unknown_headers and not missing_headers:
        passed = [
            LintResult(
                row=None,
                column=None,
                value='column-names',
                lint_test="column-names",
                message="All column names are configured correctly"
            )]
    return passed, warned, failed

def duplicate_samples(df, config):
    """Check if all columns or combination of columns contain unique IDs."""
    unique_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "unique-id"]

    unique_comb_columns = [[v['Column_name'],v['Unique_with']] for v in config.values() if 'Unique_with' in v.keys()]
    unique_comb_columns = list(set(tuple(sorted(subarray)) for subarray in unique_comb_columns))

    passed1 = []
    passed2 = []
    warned = []
    failed1 = []
    failed2 = []

    if unique_columns:
        for column in unique_columns:
            df_dupl = df.dropna(subset=[column]).copy()
            df_dupl = df_dupl[df_dupl.duplicated([column], keep=False)]
            if not df_dupl.empty:
                failed1.extend(
                    list(map(lambda row: LintResult(
                        row['Row_Number'],
                        column,
                        row[column], 
                        'duplicate-samples', 
                        f"{row[column]} is not a unique value column {column}"), 
                    df_dupl.to_dict('records')))
                )
        if not failed1:
            passed1 = [
                LintResult(
                    row=None,
                    column=None,
                    value="unique-columns",
                    lint_test="duplicate_samples",
                    message=f"No duplicates in columns {unique_columns}"
                )]
        
    if unique_comb_columns:
        for columns in unique_comb_columns: 
            df_dupl = df.dropna(subset=columns).copy()
            # The statement makes sure that we ignore the rows that we copied before as they started from another process so Id's will not be unique there 
            df_dupl = df_dupl[df_dupl['Process_started_from_LVESeqID'].isnull()]
            df_dupl = df_dupl[df_dupl.duplicated(columns, keep =False)]
            if not df_dupl.empty:
                failed2.extend(
                    list(map(lambda row: LintResult(
                        row['Row_Number'],
                        ' ,'.join(columns),
                        ' ,'.join([row.get(column) for column in columns]),
                        'duplicate-samples',
                        f"{' ,'.join([row.get(column) for column in columns])} is not a unique combination in columns {' ,'.join(columns)}"), 
                    df_dupl.to_dict('records')))
                )
        if not failed2:
            passed2 = [
                LintResult(
                    row=None,
                    column=None,
                    value="unique-combinations",
                    lint_test="duplicate-samples",
                    message=f"No duplicates of combinations in columns {unique_comb_columns}"
                )]
    passed = passed1 + passed2
    failed = failed1 + failed2
    return passed, warned, failed

def dates(df, config):
    """Check if all date columns are in the correct format."""
    date_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "date"]

    passed = []
    warned = []
    failed = []
    
    if not date_columns:
        return passed, warned, failed

    # Melt the dataframe
    melted_df = pd.melt(df[date_columns + ['Row_Number']], id_vars='Row_Number', var_name='column', value_name='value')
    
    # Drop rows with NaN values
    melted_df = melted_df.dropna()

    # Convert the value column to a datetime column
    melted_df['transformed_date'] = pd.to_datetime(melted_df['value'], errors='coerce')

    # Get the rows with NaN values
    failed_dates = melted_df[melted_df['transformed_date'].isnull()]
    if not failed_dates.empty:
        warned.extend(
            list(map(lambda row: LintResult(
                row['Row_Number'], 
                row['column'],
                row['value'], 
                'dates', 
                f"{row['value']} is not a date in column {row['column']}"), 
            failed_dates.to_dict('records')))
        )
    else:
        passed.extend([
            LintResult(
                row=None,
                column=None,
                value="non-existing-dates",
                lint_test="dates",
                message=f"All values in column {', '.join(date_columns)} are dates"
            )]
        )
    return passed, warned, failed

def unrealistic_dates(df, config):
    """Check if all date columns are in the correct format."""
    date_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "date"]

    passed = []
    warned = []
    failed = []
    
    if not date_columns:
        return passed, warned, failed

    # Melt the dataframe
    melted_df = pd.melt(df[date_columns + ['Row_Number']], id_vars='Row_Number', var_name='column', value_name='value')
    
    # Drop rows with NaN values
    melted_df = melted_df.dropna()

    # Convert the value column to a datetime column
    melted_df['transformed_date'] = pd.to_datetime(melted_df['value'], errors='coerce')

    # Define the range we want to look at
    today  = pd.to_datetime('today').floor('D')
    min_date = today - pd.DateOffset(years=6)
    
    # Filter for those that are outside the range
    failed_dates = melted_df[(melted_df['transformed_date'] < min_date) | (melted_df['transformed_date'] > today)]

    if not failed_dates.empty:
        warned.extend(
            list(map(lambda row: LintResult(
                row['Row_Number'], 
                row['column'],
                row['value'], 
                'unrealistic-dates', 
                f"{row['value']} has a questionable date in column {row['column']}"), 
            failed_dates.to_dict('records')))
        )
    else:
        passed.extend([
            LintResult(
                row=None,
                column=None,
                value="unrealistic-dates",
                lint_test="dates",
                message=f"All values in column {', '.join(date_columns)} are realistic dates"
            )]
        )
    return passed, warned, failed

def numeric_values(df, config):
    """Check if all numeric columns are in the correct format."""
    numeric_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "numeric"]

    passed = []
    warned = []
    failed = []
        
    if not numeric_columns:
        return passed, warned, failed
    # Melt the dataframe
    melted_df = pd.melt(df[numeric_columns + ['Row_Number']], id_vars='Row_Number', var_name='column', value_name='value')
    
    # Drop rows with NaN values
    melted_df = melted_df.dropna()

    # Convert the value column to a numeric column
    melted_df['transformed_value'] = pd.to_numeric(melted_df['value'], errors='coerce')

    # Get the rows with NaN values
    failed_values = melted_df[melted_df['transformed_value'].isnull()]
    if not failed_values.empty:
        warned.extend(
            list(map(lambda row: LintResult(
                row['Row_Number'], 
                row['column'],
                row['value'], 
                'numeric', 
                f"{row['value']} is not a numeric value in column {row['column']}"), 
                failed_values.to_dict('records')))
        )
    else:
        passed = [
            LintResult(
                row=None,
                column=None,
                value='non-existing-numbers',
                lint_test="numeric-values",
                message=f"All values in column {', '.join(numeric_columns)} are numeric"
            )]
    return passed, warned, failed

def presence_databaseID(df, config):
    """HARDCODED-check: check if all lassa samples have a patient ID and specimen ID."""
    passed = []
    warned = []
    failed = []
    df_lassa = df[df['Sample_Catagory'] == 'LASSA SAMPLE']
    for column in ['Database_PatientID', 'Database_idSpecimen']:
        df_lassa_subset = df_lassa[df_lassa[column].isnull()]
        if not df_lassa_subset.empty:
            failed.extend(
                list(map(lambda row: LintResult(
                    row['Row_Number'],
                    'SampleID', 
                    row['SampleID'], 
                    column, 
                    f"The lassa ID: {row['SampleID']} - was not found in the database, make sure it's written correctly (no leading zeros, correct year ...XXLVYY)"), 
                df_lassa.to_dict('records')))
            )

    if not failed :
        passed =[
            LintResult(
                row=None,
                column=None,
                value='presence-databaseID',
                lint_test="presence-databaseID",
                message="All lassa samples have a database specimen and patient ID"
            )]
    return passed, warned, failed

def referring_ids(df, config):
    """Check if the referred IDs do really exist."""
    referring_columns = [[v['Column_name'],v['Is_referring_to']] for v in config.values() if 'Is_referring_to' in v.keys() and 'Separation_character' not in v.keys()]

    passed1 = []
    passed2 = []
    warned = []
    failed1 = []
    failed2 = []
    # need to check that df[arr[0]] in df[arr[1]] exists for all arr in referring_columns
    

    if referring_columns:
        for arr in referring_columns:
            df_ref = df[df[arr[0]].notnull()].copy()
            df_ref = df_ref[~df_ref[arr[0]].isin(df[arr[1]])]
            if not df_ref.empty:
                failed1.extend(
                    list(map(lambda row: LintResult(
                        row['Row_Number'], 
                        arr[0],
                        row[arr[0]], 
                        'referring_ids', 
                        f"{row[arr[0]]} is not in {arr[1]}"), 
                    df_ref.to_dict('records')))
                )
        if not failed1:
            passed1 =[
                LintResult(
                    row=None,
                    column=None,
                    value='non-existing-ids',
                    lint_test="referring-ids",
                    message=f"All values in columns {referring_columns} refer to existing IDs"
            )]
    
    # need to check that df[arr[0]] in df[arr[1]] exists for all arr in referring_columns
    referring_columns_with_sep = [[v['Column_name'],v['Is_referring_to'],v['Separation_character']] for v in config.values() if 'Is_referring_to' in v.keys() and 'Separation_character' in v.keys()]
    if referring_columns_with_sep:
        for arr in referring_columns_with_sep:
            df_ref = df[df[arr[0]].notnull()].copy()
            df_ref['col_seperated'] = df_ref[arr[0]].str.split(arr[2])
            df_ref = df_ref.explode('col_seperated')
            df_ref = df_ref[~df_ref['col_seperated'].isin(df[arr[1]])]
            
            if not df_ref.empty:
                failed2.extend(
                    list(map(lambda row: LintResult(
                        row['Row_Number'], 
                        arr[0],
                        row[arr[0]], 
                        'referring-ids', 
                        f"The value {row['col_seperated']} from {' ,'.join(row[arr[0]].split(arr[2]))} is not in {arr[1]}"), 
                    df_ref.to_dict('records')))
                )
        if not failed2:
            passed2 = [
                LintResult(
                    row=None,
                    column=None,
                    value='non-existing-ids with seperation character',
                    lint_test="referring-ids",
                    message=f"All values refer to existing ids of columns {' ,'.join([sublist[0] for sublist in referring_columns_with_sep ])}"
                )]
    passed = passed1 + passed2
    failed = failed1 + failed2
    return passed, warned, failed 

def allowed_values(df,config):
    """Check if the values from the columns are valid, all values are expected"""
    allowed_columns = [[v['Column_name'],v['Allowed_values'].split(',')] for v in config.values() if 'Allowed_values' in v.keys()]
    passed = []
    warned = []
    failed = []

    if not allowed_columns:
        return passed, warned, failed
    
    for arr in allowed_columns:
        df_ref = df[df[arr[0]].notnull()]
        df_ref = df_ref[~df_ref[arr[0]].isin(arr[1])]
        if not df_ref.empty:
            warned.extend(
                list(map(lambda row: LintResult(
                    row['Row_Number'], 
                    arr[0],
                    row[arr[0]], 
                    'allowed-values', 
                    f"{row[arr[0]]} is not in the range of allowed values {' ,'.join(arr[1])}"), 
                df_ref.to_dict('records')))
            )
    
    if not warned:
        passed = [
            LintResult(
                row=None,
                column=None,
                value=None,
                lint_test="allowed-values",
                message=f"All values are correct in columns: {' ,'.join([sublist[0] for sublist in allowed_columns ])}"
            )]
    return passed, warned, failed