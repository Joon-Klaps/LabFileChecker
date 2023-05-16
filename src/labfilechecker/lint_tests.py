import pandas as pd
from lint_result import LintResult

def column_names(df, config):
    """Check if all column names are correct."""
    config_headers = set(v['Column_name'] for v in config.values())
    df_headers = set(df.columns)

    unknown_headers = config_headers - df_headers
    missing_headers = df_headers - config_headers

    passed = []
    warned = []
    failed = []
    if unknown_headers:
        for header in unknown_headers:
            warned.extend([
                LintResult(
                    row=None,
                    value=header,
                    lint_test="column_names",
                    message=f"Unknown column name {header}"
                )]
            )
    if missing_headers: 
        for header in missing_headers:
            failed.extend([
                LintResult(
                    row=None,
                    value=header,
                    lint_test="column_names",
                    message=f"Missing column name {header}, is not defined update config"
                )]
            )
    if not unknown_headers and not missing_headers:
        passed.extend([
            LintResult(
                row=None,
                value=None,
                lint_test="column_names",
                message="All column names are configured correctly"
            )]
        )
    return passed, warned, failed

def duplicate_samples(df, config):
    """Check if all columns or combination of columns contain unique IDs."""
    unique_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "unique-id"]

    unique_comb_columns = [[v['Column_name'],v['Unique_with']] for v in config.values() if 'Unique_with' in v.keys()]
    unique_comb_columns = list(set(tuple(sorted(subarray)) for subarray in unique_comb_columns))

    passed = []
    warned = []
    failed = []

    df = df.reset_index()

    if unique_columns:
        for column in unique_columns:
            df_dupl = df[df.duplicated([column], keep=False)]
            if not df_dupl.empty:
                failed.extend(
                    list(map(lambda row: LintResult(row['index'], row[column], 'duplicate_samples', f"{row[column]} is not a unique value in column {column}"), df_dupl.to_dict('records')))
                )
            else:
                passed.extend(
                    LintResult(
                        row=None,
                        value=column,
                        lint_test="duplicate_samples",
                        message=f"No duplicate samples in column {column}"
                    )
                )
    if not unique_comb_columns:
        for columns in unique_comb_columns: 
            df_dupl = df[df.duplicated(columns, keep =False)]
            if not df_dupl.empty:
                failed.extend(
                    list(map(lambda row: LintResult(row['index'], row[columns], 'duplicate_samples', f"{row[columns]} is not a unique combination in columns {columns}"), df_dupl.to_dict('records')))
                )
            else:
                passed.extend([
                    LintResult(
                        row=None,
                        value=columns,
                        lint_test="duplicate_samples",
                        message=f"No duplicate combinations in columns {', '.join(columns)}"
                    )]
                )
    return passed, warned, failed

def dates(df, config):
    """Check if all date columns are in the correct format."""
    date_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "date"]

    passed = []
    warned = []
    failed = []
    # Reset index, so that the index column can be used as a key later
    df = df.reset_index()

    if not date_columns:
        return passed, warned, failed

    # Melt the dataframe
    melted_df = pd.melt(df[date_columns + ['index']], id_vars='index', var_name='column', value_name='value')
    
    # Drop rows with NaN values
    melted_df = melted_df.dropna()

    # Convert the value column to a datetime column
    melted_df['transformed_date'] = pd.to_datetime(melted_df['value'], errors='coerce')

    # Get the rows with NaN values
    failed_dates = melted_df[melted_df['transformed_date'].isnull()]
    if not failed_dates.empty:
        warned.extend(
            list(map(lambda row: LintResult(row['index'], row['value'], 'dates', f"{row['value']} is not a date in column {row['column']}"), failed_dates.to_dict('records')))
        )
    else:
        passed.extend([
            LintResult(
                row=None,
                value=None,
                lint_test="dates",
                message=f"All values in column {', '.join(date_columns)} are dates"
            )]
        )
    return passed, warned, failed
def numeric_values(df, config):
    """Check if all numeric columns are in the correct format."""
    numeric_columns = [v['Column_name'] for v in config.values() if v['Column_type'] == "numeric"]

    passed = []
    warned = []
    failed = []

    # Reset index, so that the index column can be used as a key later
    df = df.reset_index()

    if not numeric_columns:
        return passed, warned, failed
    # Melt the dataframe
    melted_df = pd.melt(df[numeric_columns + ['index']], id_vars='index', var_name='column', value_name='value')
    
    # Drop rows with NaN values
    melted_df = melted_df.dropna()

    # Convert the value column to a numeric column
    melted_df['transformed_value'] = pd.to_numeric(melted_df['value'], errors='coerce')

    # Get the rows with NaN values
    failed_values = melted_df[melted_df['transformed_value'].isnull()]
    if not failed_values.empty:
        warned.extend(
            list(map(lambda row: LintResult(row['index'], row['value'], 'numeric', f"{row['value']} is not a numeric value in column {row['column']}"), failed_values.to_dict('records')))
        )
    else:
        passed.extend([
            LintResult(
                row=None,
                value=None,
                lint_test="numeric_values",
                message=f"All values in column {', '.join(numeric_columns)} are numeric"
            )]
        )
    return passed, warned, failed

def presence_patientsID(df, config):
    """HARDCODED-check: check if all lassa samples have a patient ID."""
    df = df.reset_index()
    df_lassa = df[df['Sample_Catagory'] == 'LASSA SAMPLE']
    df_lassa = df_lassa[df_lassa['Database_PatientID'].isnull()]

    passed = []
    warned = []
    failed = []
    if not df_lassa.empty:
        failed.extend(
            list(map(lambda row: LintResult(row['index'], row['SampleID'], 'presence_patientsID', f"The lassa ID: {row['SampleID']} - was not found in the database, make sure it's written correctly (no leading zeros, correct year ...XXLVYY)"), df_lassa.to_dict('records')))
        )
    else:
        passed.extend(
            [LintResult(
                row=None,
                value=None,
                lint_test="presence_patientsID",
                message="All lassa samples have a patient ID"
            )]
        )
    return passed, warned, failed

def referring_ids(df, config):
    """Check if the referred IDs do really exist."""
    referring_columns = [[v['Column_name'],v['is_referring_to']] for v in config.values() if 'is_referring_to' in v.keys() and 'seperation_character' not in v.keys()]

    passed = []
    warned = []
    failed = []
    # need to check that df[arr[0]] in df[arr[1]] exists for all arr in referring_columns
    df = df.reset_index()

    if not referring_columns:
        for arr in referring_columns:
            df_ref = df[df[arr[0]].notnull()]
            df_ref = df_ref[~df_ref[arr[0]].isin(df[arr[1]])]
            if not df_ref.empty:
                failed.extend(
                    list(map(lambda row: LintResult(row['index'], row[arr[0]], 'referring_ids', f"{row[arr[0]]} is not in {arr[1]}"), df_ref.to_dict('records')))
                )
            else:
                passed.extend([
                    LintResult(
                        row=None,
                        value=arr[0],
                        lint_test="referring_ids",
                        message=f"All values in column {arr[0]} are in {arr[1]}"
                    )]
                )
    
    referring_columns_with_sep = [[v['Column_name'],v['is_referring_to'],v['separation_character']] for v in config.values() if 'is_referring_to' in v.keys() and 'separation_character' in v.keys()]
    if not referring_columns_with_sep:
        for arr in referring_columns_with_sep:
            df_ref = df[df[arr[0]].notnull()]
            df_ref['col_seperated'] = df_ref[arr[0]].str.split(arr[2])
            df_ref = df_ref.explode('col_seperated')
            df_ref = df_ref[~df_ref['col_seperated'].isin(df[arr[1]])]
            if not df_ref.empty:
                failed.extend(
                    list(map(lambda row: LintResult(row['index'], row[arr[0]], 'referring_ids', f"The value {row['col_seperated']} from {' ,'.join(row[arr[0]].str.split(arr[2]))} is not in {arr[1]}"), df_ref.to_dict('records')))
                )
            else:
                passed.extend([
                    LintResult(
                        row=None,
                        value=arr[0],
                        lint_test="referring_ids",
                        message=f"All values in column {arr[0]} are in {arr[1]}"
                    )]
                )
    return passed, warned, failed 

def allowed_values(df,config):
    """Check if the values from the columns are valid, all values are expected"""
    allowed_columns = [[v['Column_name'],v['allowed_values'].str.split(',')] for v in config.values() if 'allowed_values' in v.keys()]
    passed = []
    warned = []
    failed = []
    df = df.reset_index()
    
    

    if not allowed_columns:
        return passed, warned, failed
    
    for arr in allowed_columns:
        df_ref = df[df[arr[0]].notnull()]
        df_ref = df_ref[~df_ref[arr[0]].isin(arr[1])]
        if not df_ref.empty:
            warned.extend(
                list(map(lambda row: LintResult(row['index'], row[arr[0]], 'allowed_values', f"{row[arr[0]]} is not in {arr[1]}"), df_ref.to_dict('records')))
            )
        else:
            passed.extend([
                LintResult(
                    row=None,
                    value=arr[0],
                    lint_test="allowed_values",
                    message=f"All values in column {arr[0]} are in {arr[1]}"
                )]
            )
    return passed, warned, failed