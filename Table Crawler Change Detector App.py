import csv
import os
import pyperclip
import warnings
from datetime import datetime

import PySimpleGUI as sg
import pandas as pd

# |||||||||||||||||||
# REFERENCE BUILDER
# |||||||||||||||||||

# list for storing status messages
message_list = []


# |||||||||||||||||||
# Function Definitions for building reference files
# |||||||||||||||||||


def all_files(directory):
    """Function to create DataFrame with all file paths,
    names, types and directories in one table,
    from a specified directory"""
    paths_list = []
    names_list = []
    types_list = []
    directories_list = []
    for path, currentDirectory, files in os.walk(directory):
        for file in files:
            my_path = os.path.join(path, file)
            filename = os.path.basename(my_path)
            paths_list.append(my_path)
            directories_list.append(os.path.split(my_path)[0])
            names_list.append(os.path.splitext(filename)[0])
            types_list.append(os.path.splitext(my_path)[-1])

    dict_of_lists = {"FilePath": paths_list,
                     "Directory": directories_list,
                     "FileName": names_list,
                     "FileType": types_list}

    combined_df = pd.DataFrame(dict_of_lists)
    return combined_df


def csv_max_col(filepath):
    """Function to get the max column length for
    a single csv file"""

    try:
        with open(filepath, newline='') as f:
            reader = csv.reader(f)
            data = list(reader)
    except:
        # See notes on this where I repeat the code below
        if "BRAND-WBC-QA LinkedIn" in filepath:
            df_1 = pd.read_csv(filepath, sep='\t', encoding="UTF-16", header=None, skiprows=5)
            # Creates a series with column counts
            data = df_1.values.tolist()
        else:
            raise Exception

    row_lengths = pd.Series([len(x) for x in data], dtype='int64')
    max_col = row_lengths.max()
    return max_col


def get_col_count(path):
    """Function to get the column count for
    a single xlsx or csv file path"""

    try:
        if ".csv" in path:
            csv_file = csv_max_col(path)
            message_list.append(''.join(["CSV Access  SUCCESS | ", path]))
            return csv_file
        elif ".xlsx" in path:
            # this code ignores some useless warnings from openpyxl
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                xlsx_df = pd.read_excel(path, engine='openpyxl')
            message_list.append(''.join(["XLSX Access SUCCESS | ", path]))
            return xlsx_df.shape[1]
        else:
            return "Unknown file type"

    except:
        if ".csv" in path:
            message_list.append(''.join(["CSV Access  FAILURE | ", path]))
        elif ".xlsx" in path:
            message_list.append(''.join(["XLSX Access FAILURE | ", path]))
        else:
            return "Unknown file type"


def add_max_cols_col(dataframe, col_name):
    """Function to add a column with max column counts
    for a provided dataframe and column, that column containing
    all file paths to be counted"""
    col_len_list = []

    for x in dataframe[col_name]:
        col_len_list.append(get_col_count(x))

    col_len_series = pd.Series(col_len_list, name='Max Column Count')

    col_len_added = pd.concat([dataframe, col_len_series], axis=1)
    return col_len_added


def get_headers_from_path(path, max_cols):
    """Returns the headers from a given csv or Excel file,
    assuming that the header is the first row containing the
    detected max amount of column values. Uses different methods
    for each file type"""
    # Grabs the csv rows as lists of data
    if ".csv" in path:
        try:
            with open(path, newline='') as f:
                reader = csv.reader(f)
                list_of_row_values = list(reader)
        except:
            """This is just to address a single LinkedIn .csv file
             I couldn't figure out. One of the top 5 rows has
             a null value that required a different csv read method. 
             So I just gave up and cut off the first 5 rows lol
             I don't fully understand why it works now"""

            if "BRAND-WBC-QA LinkedIn" in path:
                df_1 = pd.read_csv(path, sep='\t', encoding="UTF-16", header=None, skiprows=5)
                # Creates a series with column counts
                list_of_row_values = df_1.values.tolist()
            else:
                raise Exception

        def assign_header(list):
            """Looks for the first row with the max amount
            of columns and returns it"""
            for x in list:
                if len(x) == max_cols:
                    return x

        # Returns the row containing the headers as a list
        headers_list = assign_header(list_of_row_values)
        as_string = "|".join(headers_list)
        return as_string

    elif ".xlsx" in path:
        # + this code ignores some useless warnings from openpyxl
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            # Open the Excel as a DataFrame
            df_1 = pd.read_excel(path, engine='openpyxl', header=None)
        # Creates a series with column counts
        series_with_counts = df_1.count(axis='columns').rename("col_count")
        # Adds that series as a column
        df_with_counts = pd.concat([df_1, series_with_counts], axis=1)
        # Subsets df to only rows with the max cols
        only_top_max_row = df_with_counts[df_with_counts["col_count"] == max_cols]
        # Slices the df, dropping the count column and taking only the top row (AKA the headers)
        dropcol_slice = only_top_max_row.iloc[0:1, 0:int(max_cols)]
        # Returns the resulting df after making it into a list
        as_list = dropcol_slice.values.flatten().tolist()
        as_string = x = "|".join(as_list)

        return as_string
    else:
        raise Exception


def build_reference(target_dir, save_folder):
    """Function to build and save reference files of spreadsheets in a specified folder"""

    global message_list  # So Python knows to use the variable from the right scope
    message_list = []  # Clear message list

    file_details_df = all_files(target_dir)

    # Subsetting DataFrame to only xlsx and csv files
    xlsx_condition = file_details_df["FileType"] == ".xlsx"
    csv_condition = file_details_df["FileType"] == ".csv"
    # resetting the index since concat axis=1 seems to match by index
    file_details_df_subset = file_details_df[xlsx_condition | csv_condition].reset_index(drop=True)

    # Output df with column counts
    df_with_col_counts = add_max_cols_col(file_details_df_subset, "FilePath")

    # |||||||||||||||||||
    # Adding headers to reference
    # |||||||||||||||||||

    headers_list_list = []
    for index, row in df_with_col_counts.iterrows():
        try:
            headers_list = get_headers_from_path(path=row['FilePath'], max_cols=row['Max Column Count'])
            headers_list_list.append(headers_list)
        except:
            headers_list_list.append('Some error occurred')

    headers_list_series = pd.Series(headers_list_list, name="Headers List")

    header_lists_added = pd.concat([df_with_col_counts, headers_list_series], axis=1)

    # Build output file name
    RefOutputName = "/ReferenceFile"
    FileTypeName = ".csv"
    x = datetime.now()
    DateTimeString = x.strftime(" %Y-%m-%d %I-%M%p")
    joinedfilestring = ''.join([save_folder, RefOutputName, DateTimeString, FileTypeName])

    # Output to csv with no index
    header_lists_added.to_csv(joinedfilestring, index=False)


# |||||||||||||||||||
# Function for comparing two reference files
# |||||||||||||||||||

pd.set_option('display.max_rows', None, 'display.max_columns', None)


def reference_comparer(pre_ref, post_ref, cols_to_check):
    """Returns a  DataFrame showing all changed files and headers within those files
    does this using two provided reference file paths made with the other functions"""
    # Read in the reference csv files
    pre_df = pd.read_csv(pre_ref)
    post_df = pd.read_csv(post_ref)

    def same_miss_add(col_name):
        """Function to check a column in the dataframe for
        similarities, differences and additions"""

        def add_identifying_cols(my_df, match_type, check_source):
            """Function to add identifying columns to eventual output"""
            my_df["Match Type"] = match_type
            my_df["Check Source"] = check_source
            return my_df

        col_name_source_name = "Matched on " + col_name + " - Compared " + col_name + " Name"

        # File Path - Same & Missing
        left_join_df = pre_df.merge(post_df, on=col_name, how='left', indicator=True)
        left_join_df_identified_renamed = left_join_df.rename(columns={col_name: 'Value'})

        same_bool = left_join_df_identified_renamed['_merge'] == 'both'
        same_join_new_cols = add_identifying_cols(left_join_df_identified_renamed, "In both references",
                                                  col_name_source_name)
        same_join_final = same_join_new_cols.loc[same_bool, ['Value', "Match Type", "Check Source"]]

        left_bool = left_join_df_identified_renamed['_merge'] == 'left_only'
        left_join_new_cols = add_identifying_cols(left_join_df_identified_renamed, "Missing in new reference",
                                                  col_name_source_name)
        left_join_final = left_join_new_cols.loc[left_bool, ['Value', "Match Type", "Check Source"]]

        # File Path - Added
        right_join_df = pre_df.merge(post_df, on=col_name, how='right', indicator=True)
        right_join_df_identified = add_identifying_cols(right_join_df, "Added in new ref file", col_name_source_name)
        right_join_df_identified_renamed = right_join_df_identified.rename(columns={col_name: 'Value'})

        right_bool = right_join_df_identified['_merge'] == 'right_only'
        right_join_final = right_join_df_identified_renamed.loc[right_bool, ['Value', "Match Type", "Check Source"]]

        concat_results = pd.concat([same_join_final,
                                    left_join_final,
                                    right_join_final])

        return concat_results

    # |||||||||||||||||||||
    # ||| Running name checks functions |||
    # |||||||||||||||||||||

    # Initialise the list of DataFrames to concat
    name_checks_list = []

    # Perform the reference checking actions for each column provided
    for x in cols_to_check:
        name_checks_list.append(same_miss_add(x))

    # Concat them all together
    multi_concat = pd.concat(name_checks_list)

    # Sorting on Check Source and then Match Type
    multi_concat_sorted = multi_concat.sort_values(["Check Source", "Match Type"])

    # Defining final output variable
    path_compare_final = multi_concat_sorted

    # |||||||||||||||||||||
    # ||| Header Difference Detection|||
    # |||||||||||||||||||||

    # Subsetting the pre and post reference files and then merging on FilePath
    headers_to_select = ["FilePath", 'Headers List']

    pre_subset = pre_df[headers_to_select]
    post_subset = post_df[headers_to_select]

    pre_post_merge = pre_subset.merge(post_subset, on="FilePath", how='inner',
                                      suffixes=('_pre', '_post'))

    # Converting Dataframes to a Dictionary of lists for comparison work
    comparison_dict = pre_post_merge.to_dict(orient='list')

    # Splitting contained data into list objects
    comparison_dict['Headers List_post'] = [x.split("|") for x in comparison_dict['Headers List_post']]
    comparison_dict['Headers List_pre'] = [x.split("|") for x in comparison_dict['Headers List_pre']]

    # Taking out the lists from the dictionary as just lists for ease of use
    headers_pre_list_list = comparison_dict['Headers List_pre']
    headers_post_list_list = comparison_dict['Headers List_post']

    # Looping through dictionary to compare differences and adding results to dict

    # Defining dictionary to capture results with
    col_diff_dict = {'Header Value': [],
                     'Match Type': [],
                     'Check Source': [],
                     'Index': []}

    def append_result(value, match, source):
        """Function to append a result to the result dictionary"""
        col_diff_dict['Header Value'].append(value)
        col_diff_dict['Match Type'].append(match)
        col_diff_dict['Check Source'].append(source)

    # Checking between the new lists, matching header lists using the enumerate index
    # Adding index to dictionary for merging with source data later
    for index, header_list in enumerate(headers_post_list_list):
        for header in header_list:

            if header in headers_pre_list_list[index]:
                append_result(header, "In both references", "Matched on FilePath - Compared Headers")
                col_diff_dict['Index'].append(index)

            if header not in headers_pre_list_list[index]:
                append_result(header, "Added in new ref file", "Matched on FilePath - Compared Headers")
                col_diff_dict['Index'].append(index)

    for index, header_list in enumerate(headers_pre_list_list):
        for header in header_list:

            if header not in headers_post_list_list[index]:
                append_result(header, "Missing in new reference", "Matched on FilePath - Compared Headers")
                col_diff_dict['Index'].append(index)

    # Converting the results into a DataFrame
    headers_differences_df = pd.DataFrame(col_diff_dict).set_index("Index")

    # Joining that table back with the source table to get the paths of the source match
    # Using index numbers to join since they are the same
    headers_diff_full = pd.merge(headers_differences_df,
                                 pre_post_merge,
                                 left_index=True,
                                 right_index=True,
                                 how='left')

    # Subsetting to drop unwanted columns
    cols_to_subset = ["Header Value", "Match Type", "Check Source", "FilePath"]
    headers_diff_full_subset = headers_diff_full[cols_to_subset]

    # Sorting by FilePath then Match Type
    headers_diff_full_sorted = headers_diff_full_subset.sort_values(["FilePath", "Match Type"])

    # Renaming FilePath column name
    headers_diff_full_sorted.rename(columns={'FilePath': 'Value'}, inplace=True)

    # Defining final output variable
    headers_diff_final = headers_diff_full_sorted

    # |||||||||||||||||||||
    # ||| Combining with file cross check results|||
    # |||||||||||||||||||||

    # Concatenating them together
    compare_output_final = pd.concat([path_compare_final, headers_diff_final])

    # Removing rows where no difference was found
    compare_output_final_diffs_only = compare_output_final[compare_output_final['Match Type'] != "In both references"]

    # Using a copy to avoid the SettingWithCopyWarning
    compare_output_final_diffs_only = compare_output_final_diffs_only.copy()

    # Renaming Match Type Values
    compare_output_final_diffs_only['Match Type'].replace(['Added in new ref file', 'Missing in new reference'],
                                                          ['New', 'Missing'],
                                                          inplace=True)

    # Sorting results
    compare_output_final_diffs_only_sorted = compare_output_final_diffs_only.sort_values(["Check Source", "Match Type"])

    # Resetting Index
    compare_output_final_diffs_only_sorted.reset_index(drop=True, inplace=True)

    # Defining final output
    all_diffs_final = compare_output_final_diffs_only_sorted

    return all_diffs_final


# |||||||||||||||||||||||||||
# Function to format timedelta
# |||||||||||||||||||||||||||

# Notes from the template I copied for reference
"""
    Demo Combo File Chooser - with clearable history

    This is a design pattern that is very useful for programs that you run often that requires
    a filename be entered.  You've got 4 options to use to get your filename with this pattern:
    1. Copy and paste a filename into the combo element
    2. Use the last used item which will be visible when you create the window
    3. Choose an item from the list of previously used items
    4. Browse for a new name

    To clear the list of previous entries, click the "Clear History" button.

    The history is stored in a json file using the PySimpleGUI User Settings APIs

    The code is as sparse as possible to enable easy integration into your code.

    Copyright 2021 PySimpleGUI
"""

def human_delta(tdelta):
    """
    Takes a timedelta object and formats it for humans.
    Usage:
        # 149 day(s) 8 hr(s) 36 min 19 sec
        print human_delta(datetime(2014, 3, 30) - datetime.now())
    Example Results:
        23 sec
        12 min 45 sec
        1 hr(s) 11 min 2 sec
        3 day(s) 13 hr(s) 56 min 34 sec
    :param tdelta: The timedelta object.
    :return: The human formatted timedelta
    """
    d = dict(days=tdelta.days)
    d['hrs'], rem = divmod(tdelta.seconds, 3600)
    d['min'], d['sec'] = divmod(rem, 60)

    if d['min'] == 0:
        fmt = '{sec} sec'
    elif d['hrs'] == 0:
        fmt = '{min} min {sec} sec'
    elif d['days'] == 0:
        fmt = '{hrs} hr(s) {min} min {sec} sec'
    else:
        fmt = '{days} day(s) {hrs} hr(s) {min} min {sec} sec'

    return fmt.format(**d)


# |||||||||||||||||||
# THE UI VIA PYSIMPLEGUI
# |||||||||||||||||||


# |||||||||||||||||||||||||||
# DEFINING THE LAYOUT
# |||||||||||||||||||||||||||

layout = [
    # Row 1-2
    # Saved path ref = -dir_path-
    # Last File Name = '-last_dir_name-'
    # Clear History = Clear Dir History
    # Key = -DIR_PATH_FILE-
    [sg.Text("DIRECTORY PATH - Build the reference from here")],

    [sg.Combo(sorted(sg.user_settings_get_entry('-dir_path-', [])),
              default_value=sg.user_settings_get_entry('-last_dir_name-', ''), size=(175, 1), key='-DIR_PATH_FILE-'),
     sg.FolderBrowse(), sg.B('Clear Dir History')],

    # Row 3-4
    # Saved path ref = -ref_output-
    # Last File Name = '-last_ref_output_name-'
    # Clear History = Clear Ref Output History
    # Key = -REF_OUTPUT_PATH_FILE-
    [sg.Text("REFERENCE OUTPUT LOCATION - Save the reference file here")],

    [sg.Combo(sorted(sg.user_settings_get_entry('-ref_output-', [])),
              default_value=sg.user_settings_get_entry('-last_ref_output_name-', ''), size=(175, 1),
              key='-REF_OUTPUT_PATH_FILE-'),
     sg.FolderBrowse(), sg.B('Clear Ref Output History')],

    # Row 5-6
    # Saved path ref = -expected_ref_path-
    # Last File Name = '-last_expected_ref_name-'
    # Clear History = Clear Expected Ref History
    # Key = -EXPECTED_REF_PATH_FILE-
    [sg.Text("EXPECTED - Path of reference file to use as the template")],

    [sg.Combo(sorted(sg.user_settings_get_entry('-expected_ref_path-', [])),
              default_value=sg.user_settings_get_entry('-last_expected_ref_name-', ''), size=(175, 1),
              key='-EXPECTED_REF_PATH_FILE-'),
     sg.FileBrowse(), sg.B('Clear Expected Ref History')],

    # Row 7-8
    # Saved path ref = -actual_ref_path-
    # Last File Name = '-last_actual_ref_name-'
    # Clear History = Clear Actual Ref History
    # Key = -ACTUAL_REF_PATH_FILE-
    [sg.Text("ACTUAL - Path of reference file to compare against expected")],

    [sg.Combo(sorted(sg.user_settings_get_entry('-actual_ref_path-', [])),
              default_value=sg.user_settings_get_entry('-last_actual_ref_name-', ''), size=(175, 1),
              key='-ACTUAL_REF_PATH_FILE-'),
     sg.FileBrowse(), sg.B('Clear Actual Ref History')],

    # Row 9-10
    # Saved path ref = -comparison_path-
    # Last File Name = '-last_comparison_name-'
    # Clear History = Clear Comparison History
    # Key = -COMPARISON_PATH_FILE-
    [sg.Text("COMPARISON OUTPUT LOCATION - Save the comparison file here")],

    [sg.Combo(sorted(sg.user_settings_get_entry('-comparison_path-', [])),
              default_value=sg.user_settings_get_entry('-last_comparison_name-', ''), size=(175, 1),
              key='-COMPARISON_PATH_FILE-'),
     sg.FolderBrowse(), sg.B('Clear Comparison History')],

    # Row 11
    [sg.HorizontalSeparator()],

    # Row 12
    [sg.Text('Awaiting Input', font=('Helvetica', 20), text_color='green', background_color='white', key='-STATUS-'),
     sg.Text("Script run time will appear here", key='-RUNTIME-'),
     sg.Text("Output dialogue not yet available", text_color='orange', key='-OUTPUTDIALOGUE-')],

    # Row 13
    [sg.Button('Build Reference File'),
     sg.Button('Build Comparison File'),
     sg.Button('Copy Output Dialogue to Clipboard'),
     sg.Button('Save History'),
     sg.Button('Exit & Save History'),
     sg.Button('Cancel'),
     sg.VerticalSeparator()]

]


# |||||||||||||||||||||||||||
# RUNNING THE WINDOW
# |||||||||||||||||||||||||||


def save_all_histories():
    """Function to save all histories so I can repeat it elsewhere"""
    # If Exit & Save, then need to add the filename to the list of files and also set as the last used filename

    # Dir Path Saves
    sg.user_settings_set_entry('-dir_path-',
                               list(set(sg.user_settings_get_entry('-dir_path-', []) + [
                                   values['-DIR_PATH_FILE-'], ])))
    sg.user_settings_set_entry('-last_dir_name-', values['-DIR_PATH_FILE-'])

    # Ref Output Saves
    sg.user_settings_set_entry('-ref_output-',
                               list(set(sg.user_settings_get_entry('-ref_output-', []) + [
                                   values['-REF_OUTPUT_PATH_FILE-'], ])))
    sg.user_settings_set_entry('-last_ref_output_name-', values['-REF_OUTPUT_PATH_FILE-'])

    # Expected Ref Template Saves
    sg.user_settings_set_entry('-expected_ref_path-',
                               list(set(sg.user_settings_get_entry('-expected_ref_path-', []) + [
                                   values['-EXPECTED_REF_PATH_FILE-'], ])))
    sg.user_settings_set_entry('-last_expected_ref_name-', values['-EXPECTED_REF_PATH_FILE-'])

    # Actual Ref Template Saves
    sg.user_settings_set_entry('-actual_ref_path-',
                               list(set(sg.user_settings_get_entry('-actual_ref_path-', []) + [
                                   values['-ACTUAL_REF_PATH_FILE-'], ])))
    sg.user_settings_set_entry('-last_actual_ref_name-', values['-ACTUAL_REF_PATH_FILE-'])

    # Comparison Path Saves
    sg.user_settings_set_entry('-comparison_path-',
                               list(set(sg.user_settings_get_entry('-comparison_path-', []) + [
                                   values['-COMPARISON_PATH_FILE-'], ])))
    sg.user_settings_set_entry('-last_comparison_name-', values['-COMPARISON_PATH_FILE-'])


window = sg.Window('Directory Spreadsheet Change Checker', layout)

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Cancel'):
        break

    if event == 'Save History':
        save_all_histories()

    if event == 'Exit & Save History':
        save_all_histories()
        break

    # Clear buttons

    elif event == 'Clear Dir History':
        sg.user_settings_set_entry('-dir_path-', [])
        sg.user_settings_set_entry('-last_dir_name-', '')
        window['-DIR_PATH_FILE-'].update(values=[], value='')

    elif event == 'Clear Ref Output History':
        sg.user_settings_set_entry('-ref_output-', [])
        sg.user_settings_set_entry('-last_ref_output_name-', '')
        window['-REF_OUTPUT_PATH_FILE-'].update(values=[], value='')

    elif event == 'Clear Expected Ref History':
        sg.user_settings_set_entry('-expected_ref_path-', [])
        sg.user_settings_set_entry('-last_expected_ref_name-', '')
        window['-EXPECTED_REF_PATH_FILE-'].update(values=[], value='')

    elif event == 'Clear Actual Ref History':
        sg.user_settings_set_entry('-actual_ref_path-', [])
        sg.user_settings_set_entry('-last_actual_ref_name-', '')
        window['-ACTUAL_REF_PATH_FILE-'].update(values=[], value='')

    elif event == 'Clear Comparison History':
        sg.user_settings_set_entry('-comparison_path-', [])
        sg.user_settings_set_entry('-last_comparison_name-', '')
        window['-COMPARISON_PATH_FILE-'].update(values=[], value='')

    # Buttons that perform actions

    elif event == 'Build Reference File':

        startTime = datetime.now()

        window['-STATUS-'].update(value='BUILDING REFERENCE FILE', text_color='red')
        window.refresh()

        # ||| Run Function BELOW here |||

        save_all_histories()

        # Variables from input
        directory_path = values["-DIR_PATH_FILE-"]
        ref_save_loc = values["-REF_OUTPUT_PATH_FILE-"]

        # Building the reference file and saving it with function
        build_reference(directory_path, ref_save_loc)

        # Copying output dialogue to clip board
        pyperclip.copy('\n'.join(message_list))

        # Updating Output Dialogue
        window['-OUTPUTDIALOGUE-'].update(value="Output dialogue available")
        window.refresh()

        # ||| Run Function ABOVE here |||

        endTime = datetime.now() - startTime
        endTime_formatted = human_delta(endTime)
        endTime = "Reference file build task complete in " + endTime_formatted

        window['-STATUS-'].update(value='IDLE', text_color='green')
        window['-RUNTIME-'].update(value=endTime)

        window.refresh()

    elif event == 'Build Comparison File':

        startTime = datetime.now()

        window['-STATUS-'].update(value='BUILDING COMPARISON FILE', text_color='red')
        window.refresh()

        # ||| Run Function BELOW here |||

        save_all_histories()

        # Variables from input
        expected_file_path = values["-EXPECTED_REF_PATH_FILE-"]
        actual_file_path = values["-ACTUAL_REF_PATH_FILE-"]
        comparison_save_path = values["-COMPARISON_PATH_FILE-"]

        # Build output file name / path
        RefOutputName = "/ComparisonFile"
        FileTypeName = ".csv"
        x = datetime.now()
        DateTimeString = x.strftime(" %Y-%m-%d %I-%M%p")
        joinedfilestring = ''.join([comparison_save_path, RefOutputName, DateTimeString, FileTypeName])

        # Build the comparison DataFrame
        comparison_df = reference_comparer(expected_file_path, actual_file_path, ("FilePath", "Directory", "FileName"))

        # Write the DataFrame as a csv to the specified location
        comparison_df.to_csv(joinedfilestring)

        # ||| Run Function ABOVE here |||

        endTime = datetime.now() - startTime
        endTime_formatted = human_delta(endTime)
        endTime = "Comparison file build task complete in " + endTime_formatted

        window['-STATUS-'].update(value='IDLE', text_color='green')
        window['-RUNTIME-'].update(value=endTime)

        window.refresh()

window.close()
