'''
update_mapping_summary.py

Outputs a txt file with the mapping summary described in variablemap.csv in a slightly more human readable form
'''

import pandas as pd
import numpy as np
import os
from tqdm import tqdm

# Store the file name of all csvs in processed

filepaths = [f for f in os.listdir("/home/jovyan/ODBiz/1-PreProcessing/processed/") if f.endswith('.csv') and not(f.startswith('.'))]
print(f"Indicies of filepaths: 0...{len(filepaths)-1}")
filepaths.sort()
filepaths = filepaths#[:-1]

# =========================================================================================

# Outputs the number of columns from all csvs that have a mapping in variable_mapping.csv 
# Displays the unmapped columns
# Displays variables that aren't defined in the csv but are present in variable map

def write_and_print(filepath: str, text: str, mode = 'a'):
    '''
    Prints out the `text` and writes it to the file specified in `filepath`
    '''
    # print(text)
    with open(filepath, mode) as f:
        f.write(text + '\n')

# Define file paths
vm_csv_path = "/home/jovyan/ODBiz/2-OpenTabulate/variablemap.csv"
txt_path = '/home/jovyan/ODBiz/2-OpenTabulate/mapping_summary.txt'
unmapped_path = '/home/jovyan/ODBiz/2-OpenTabulate/unmapped_vars.csv'

# Read in variablemap.csv
vm_df = pd.read_csv(vm_csv_path)
vm_df = vm_df.set_index('localfile')

# Create the unmapped_path csv
um_df = pd.DataFrame(columns=['localfile', 'Unmapped_Variables'])
um_df = um_df.set_index('localfile')

# Overwrite the summary file
with open(txt_path, 'w') as f:
    f.write('')
print(f'Summary successfully rewritten to {txt_path}')

# Loop through all csv file names
no_of_files = len(filepaths)
print('Updating file...')
for i in tqdm(range(no_of_files)):
    write_and_print(txt_path, '\n========================================================\n')
    localfile = filepaths[i]
    write_and_print(txt_path, f"Now viewing summary of [{i+1}] {localfile}:\n")
    csv_path = f"/home/jovyan/ODBiz/1-PreProcessing/processed/{localfile}"

    # Import the csv as dataframe
    df = pd.read_csv(csv_path, low_memory=False)

    # Extract the necessary column/row
    df_cols = df.columns
    mapped_cols = vm_df.loc[localfile]

    # Take the intersection
    shared_cols = df_cols.intersection(mapped_cols.values)

    # Count how many were mapped
    tot_cols = len(df_cols)
    tot_mapped = len(shared_cols)
    write_and_print(txt_path, f'{tot_mapped} out of {tot_cols} columns were mapped:')

    # Display the mappings
    max_col_len = max(list(map(len, shared_cols.to_list() + [i for i in mapped_cols if (type(i) == str and 'force:' in i)])))
    for idx, val in mapped_cols.iteritems():
        if val in shared_cols or (type(val) == str and 'force:' in val):
            val_len = len(val)
            val += (max_col_len-val_len) * ' '
            write_and_print(txt_path, f'{val} -> {idx}')

    # Display unmapped columns 
    diff = ~(df_cols.isin(shared_cols))
    missing = df_cols[diff]
    missing = missing.sort_values()
    missing_len = len(missing)
    write_and_print(txt_path, '\n-----------------------')
    write_and_print(txt_path, f'There are {missing_len} unmapped columns:')
    # if missing.size == 0:
    #     write_and_print(txt_path, "No unmapped columns")
    # else:
    for i in missing:
        write_and_print(txt_path, i)

    # Save unknown variables to a csv
    um_df.loc[localfile, 'Unmapped_Variables'] = ',\n'.join(missing)

    # Display variables in variablemap.csv that aren't in the processed dataset
    mapped_cols2 = mapped_cols.drop(['source_url', 'provider', 'licence', 'last_updated', 'update_frequency', 'notes'])
    unk_var_idx = []
    unk_var_val = []
    for idx, val in mapped_cols2.iteritems():
        if type(val) == str and not( ('force:' in val) or (val in df_cols) ):
            unk_var_idx.append(idx)
            unk_var_val.append(val)
    unk_var_len = len(unk_var_idx)

    # Print out the unknown variables
    write_and_print(txt_path, '\n-----------------------')
    write_and_print(txt_path, f'There are {unk_var_len} unknown variables:')
    # if unk_var_idx == []:
    #     write_and_print(txt_path, '<empty>')
    # else:
    try:
        max_col_len = max(list(map(len, unk_var_val)))
    except:
        pass
    for j in range(len(unk_var_val)):
        val = unk_var_val[j]
        idx = unk_var_idx[j]
        val_len = len(val)
        val += (max_col_len-val_len) * ' '
        write_and_print(txt_path, f'{val} -> {idx}')

    write_and_print(txt_path, f'\nFlagging messages:')
    flag_msg = ''
    if tot_mapped != tot_cols:
        flag_msg += '- NOT_ALL_COLS_MAPPED\n' # Not all columns were mapped
    if unk_var_len != 0:
        flag_msg += '- UNK_VARS_EXIST\n' # Unknown variables exist
    
    write_and_print(txt_path, f'{flag_msg}')
    # print(f'Summary successfully appended to {txt_path}')
um_df.to_csv(unmapped_path)
print(f'Saved unmapped variables to {unmapped_path}')
print('DONE')