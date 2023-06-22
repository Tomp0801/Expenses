from inout import read_all_expenses, read_categories, ask_choice
from utils import get_kw_args, read_expenses, lower_no_space, find_keyword, collect_expenses
import json
import numpy as np
from datetime import datetime

class Categorizer:
    def __init__(self, folder, config) -> None:
        self._config = config
        self._df = read_all_expenses(folder, date_column=config["date_column"], 
                                     delimiter=config["delimiter"], encoding=config["encoding"])
        self._categories_file = config["categories_file"]
        self._categories = read_categories(config["categories_file"])
        self._df_expenses = self.read_expenses(self._df)
    
    def complete(self, save=True):
        expenses, indices_not_found = self.collect()
        indices = self.categorize(indices_not_found, self._categories, save_categories=save)
        missing_expenses = self._df_expenses.loc[indices]
        return missing_expenses
        
    def categorize(self, indices, categories, save_categories=True):
        categorized_indices = []
        for i in indices:
            amount = self._df_expenses.loc[i, self._config["amount_column"]]
            sender = self._df_expenses.loc[i, self._config["purpose_column"]]
            purpose = self._df_expenses.loc[i, self._config["name_column"]]
            print(f"Not found: {sender} - {purpose} : {amount}")
            new_cat, cat_is_new = ask_choice("Enter category:", np.unique(list(categories.keys())))
            if new_cat is None:
                new_keyword = lower_no_space(purpose)
                new_cat = "Ignored"
            elif new_cat == "":
                #new_cat = "Verschiedenes"
                continue
            else:
                new_keyword = None
                while new_keyword is None or not find_keyword(new_keyword, [sender, purpose]): 
                    new_keyword = input("Type in keyword to recognize similar entries: ")
            
            if not new_cat in list(categories.keys()):
                categories[new_cat] = []
            categories[new_cat].append(new_keyword)
            categorized_indices.append(i)
            if save_categories:
                with open(self._categories_file, "w") as f:
                    json.dump(categories, f, indent=4)
        return categorized_indices
    
    def collect(self, expenses={}):
        indices_not_found = []
        for i, row in self._df_expenses.iterrows():
            found = False
            for cat_name in self._categories.keys():
                #print(cat)
                #print(row["Verwendungszweck"].lower().replace(" ", ""))
                purpose = row[self._config["purpose_column"]]
                sender = row[self._config["name_column"]]
                cat_keywords = self._categories[cat_name]
                for keyword in cat_keywords:
                    if find_keyword(keyword, [sender, purpose]):
                        found = True
                        Categorizer.add_expense_to_category(expenses, cat_name, row[self._config["amount_column"]], keyword)
                        #print(row["Auftraggeber/Empfänger"], row["Verwendungszweck"])
            if not found:
                indices_not_found.append(i)
        return expenses, indices_not_found
    
    @staticmethod
    def add_expense_to_category(all_cats, cat_name, amount, keyword):
        if not cat_name in all_cats.keys():
            all_cats[cat_name] = {"total": 0.0, "amounts":[], "labels":[]}
        all_cats[cat_name]["total"] += -amount
        all_cats[cat_name]["amounts"].append(-amount)
        all_cats[cat_name]["labels"].append(keyword)

    def read_expenses(self, df):
        negative = self._config["outgoing"]=="True"
        positive = self._config["incoming"]=="True"
        amount = self._config["amount_column"]
        for i, row in df.iterrows():
            betrag = row[amount].replace(".", "")
            betrag = betrag.replace(",", ".")
            df.at[i, amount] = float(betrag)
        if negative and not positive:
            df = df[df[amount] <= 0]
        elif not negative and positive:
            df = df[df[amount] >= 0]
        elif not negative and not positive:
            print("Error: Selected neither negative nor positive transactions")
        df = df[df[self._config["name_column"]] != self._config["name"]]
        df.reset_index(inplace=True, drop=True)
        return df

    def get_week_count(self):
        df = self._df_expenses
        date_col = self._config["date_column"]
        date_f = self._config["date_format"]
        if date_f.lower()=="dmy":
            date_f = "%d.%m.%Y"
        elif date_f.lower()=="ymd":
            date_f = "%Y.%m.%d"
        elif date_f.lower()=="mdy":
            date_f = "%m.%d.%Y"
        elif date_f.lower()=="ydm":
            date_f = "%Y.%d.%m"
        else:
            date_f = "%d.%m.%Y"
        start = datetime.strptime(df[date_col][len(df)-1], date_f)
        stop = datetime.strptime(df[date_col][0], date_f)
        return (stop - start).days / 7