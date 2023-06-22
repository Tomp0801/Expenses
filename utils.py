from datetime import datetime
import pandas as pd
import configparser

def get_kw_args(file, section):
    config = configparser.ConfigParser()
    config.read(file)
    args = dict(config[section])
    # auto type conversion
    for k, v in args.items():
        if v=="True":
            args[k] = True
        if v=="False":
            args[k] = False
        try:
            args[k] = int(v)
        except:
            pass
    return args

def lower_no_space(string):
    return string.lower().replace(" ","")
    
def find_keyword(keyword, strings):
    for s in strings:
        if keyword in lower_no_space(s):
            return True
    return False

def divide_df(df, time_col="Buchung"):
    df["Monat"] = None
    for i, row in df.iterrows():
        date = datetime.strptime(row[time_col], "%d.%m.%Y")
        df.at[i, "Monat"] = date.year * 12 + date.month
    months = df["Monat"].unique()
    dfs = []
    dates = []
    for m in months:
        dfs.append(df[df["Monat"] == m])
        dates.append(datetime(year=m // 12, month=m%12+1, day=1))
    return dates, dfs

def add_expense_to_category(all_cats, cat_name, amount, keyword):
    if not cat_name in all_cats.keys():
        all_cats[cat_name] = {"total": 0.0, "amounts":[], "labels":[]}
    all_cats[cat_name]["total"] += -amount
    all_cats[cat_name]["amounts"].append(-amount)
    all_cats[cat_name]["labels"].append(keyword)

def add_up_expenses(expenses):
    cats = []
    totals = []
    labels = []
    for key, val in expenses.items():
        if key != "Ignored":
            cats.append(key)
            totals.append(val["total"])
            labels.append(val["labels"])
    return cats, totals, labels

def condense_amounts(labels, amounts):
    condensed = {}
    for i, label in enumerate(labels):
        if not label in condensed:
            condensed[label] = 0
        condensed[label] += amounts[i]
    return list(condensed.keys()), list(condensed.values())
