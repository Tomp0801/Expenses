from datetime import datetime
import pandas as pd

def get_start_date(df):
    return datetime.strptime(df["Buchung"][len(df)-1], "%d.%m.%Y")

def get_end_date(df):
    return datetime.strptime(df["Buchung"][0], "%d.%m.%Y")

def get_week_count(df):
    return (get_end_date(df) - get_start_date(df)).days / 7

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


def collect_expenses(df, categories, expenses={}):
    indices_not_found = []
    for i, row in df.iterrows():
        found = False
        for cat_name in categories.keys():
            #print(cat)
            #print(row["Verwendungszweck"].lower().replace(" ", ""))
            purpose = row["Verwendungszweck"]
            sender = row["Auftraggeber/Empfänger"]
            cat_keywords = categories[cat_name]
            for keyword in cat_keywords:
                if find_keyword(keyword, [sender, purpose]):
                    found = True
                    add_expense_to_category(expenses, cat_name, row["Betrag"], keyword)
                    #print(row["Auftraggeber/Empfänger"], row["Verwendungszweck"])
        if not found:
            indices_not_found.append(i)
    return expenses, indices_not_found

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

def read_expenses(df, only_negative=True):
    for i, row in df.iterrows():
        betrag = row["Betrag"].replace(".", "")
        betrag = betrag.replace(",", ".")
        df.at[i, "Betrag"] = float(betrag)
    if only_negative:
        df = df[df["Betrag"] <= 0]
    df = df[df["Auftraggeber/Empfänger"] != "Thomas Pfitzinger"]
    df.reset_index(inplace=True, drop=True)
    return df