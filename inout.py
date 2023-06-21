from utils import find_keyword, lower_no_space
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime

def read_expense_file(file, date_column, delimiter=",", encoding="utf-8"):
    """Read a csv file containing expenses.

    Args:
        file (str): File name.
        date_column (str): Name of the column containing dates.
        delimiter (str, optional): Delimiter between cells. Defaults to ",".
        encoding (str, optional): File encoding. Defaults to "utf-8".

    Returns:
        pd.DataFrame: The read data in a dataframe.
    """
    df = pd.read_csv(file, delimiter=delimiter, encoding=encoding)
    df["timestamp"] = None
    for i in range(len(df)):
        df.at[i, "timestamp"] = datetime.strptime(df.loc[i, date_column], "%d.%m.%Y").timestamp()
    return df

def read_all_expenses(path, date_column, delimiter=",", encoding="utf-8"):
    """Read all expenses-csv files in a directory.

    Args:
        path (str): The directory.
        date_column (str): Name of the column containing dates.
        delimiter (str, optional): Delimiter between cells. Defaults to ",".
        encoding (str, optional): File encoding. Defaults to "utf-8".

    Returns:
        pd.DataFrame: The read data in a dataframe.
    """
    base_df = None
    for file in sorted(os.listdir(path)):
        _file = os.path.join(path, file)
        if os.path.isdir(_file) or not _file.endswith(".csv"):
            continue
        df = read_expense_file(_file, date_column, delimiter, encoding)
        if base_df is None:
            base_df = df
        else:
            last_date = np.max(base_df["timestamp"])
            df = df[(df["timestamp"] > last_date)]
            base_df = pd.concat([base_df, df], ignore_index=True)
    return base_df.sort_values(by="timestamp").reset_index(drop=True)


def read_categories(file="categories.json"):
    """Read the file containing saved categories.

    Args:
        file (str, optional): The file name. Defaults to "categories.json".

    Returns:
        dict: Dictionary of categories and keywords.
    """
    if os.path.exists(file):
        with open(file, "r") as f:
            categories = json.load(f)
        return categories
    else:
        print(f"Error: file {file} not found")
        return {}

def ask_choice(message, choices):
    """Prompt the user to choose an entry from a given list,
    or to enter a new option.

    Args:
        message (str): Message to the user.
        choices (list): Answer options for the user.

    Returns:
        str, bool: The user's answer and True, if the answer is new 
        (not contained in choices).
    """
    print(message)
    for i in range(len(choices)):
        print(f"{i}: {choices[i]}")
    print(f"#: Ignore")
    answer = input("Enter number or type in new choice: ")
    try:
        if answer == "#":
            return None, False
        i = int(answer)
        return choices[i], False
    except:
        return answer, True
