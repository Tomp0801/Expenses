from importing.inout import read_all_expenses, read_categories, ask_choice
from categorizing.utils import get_date_format, find_keyword, flatten_categories
import json
import numpy as np
from datetime import datetime
import os



class Categorizer:
    def __init__(self, folder, config, depth=1) -> None:
        self._config = config
        self._df = read_all_expenses(folder, date_column=config["date_column"], 
                                     delimiter=config["delimiter"], encoding=config["encoding"])
        self._categories_file = os.path.join(folder, config["categories_file"])
        self._categories = flatten_categories(read_categories(self._categories_file), depth=depth)
        self._df_expenses = self.read_expenses(self._df)
        
    def complete(self, save=True):
        expenses, indices_not_found = self.collect()
        indices = self.categorize(indices_not_found, self._categories, save_categories=save)
        missing_expenses = self._df_expenses.loc[indices]
        return missing_expenses
        
    def categorize(self, indices, categories, save_categories=True):
        categorized_indices = []
        for i in indices:
            amount = float(self._df_expenses.loc[i, self._config["amount_column"]])
            sender = str(self._df_expenses.loc[i, self._config["name_column"]])
            purpose = str(self._df_expenses.loc[i, self._config["purpose_column"]])
            if self.find_category(purpose + sender):
                continue
            print(f"Not found: {sender} - {purpose} : {amount}")
            new_cat, cat_is_new = ask_choice("Enter category:", np.unique(list(categories.keys())))
            if new_cat is None:
                new_keyword = purpose.replace(" ", "")
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
    
    def find_category(self, description):
        for cat_name in self._categories.keys():
            cat_keywords = self._categories[cat_name]
            for keyword in cat_keywords:
                if find_keyword(keyword, [description]):
                    return cat_name
        return None

    def collect(self, df=None, expenses={}, depth=0):
        if df is None:
            df = self._df_expenses
        indices_not_found = []
        for i, row in df.iterrows():
            found = False
            for cat_name in self._categories.keys():
                purpose = row[self._config["purpose_column"]]
                sender = row[self._config["name_column"]]
                cat_keywords = self._categories[cat_name]
                for keyword in cat_keywords:
                    if find_keyword(keyword, [sender, purpose]):
                        found = True
                        Categorizer.add_expense_to_category(expenses, cat_name, row[self._config["amount_column"]], keyword)
                        # TODO use find_category
                        #print(row["Auftraggeber/Empfänger"], row["Verwendungszweck"])
            if not found:
                indices_not_found.append(i)
        return expenses, indices_not_found

    def divide_by_months(self, month_col="Month"):
        time_col = self._config["date_column"]
        date_f = get_date_format(self._config["date_format"])
        self._df_expenses[month_col] = None
        for i, row in self._df_expenses.iterrows():
            date = datetime.strptime(row[time_col], date_f)
            self._df_expenses.at[i, month_col] = date.year * 12 + date.month
        months = self._df_expenses[month_col].unique()
        dfs = []
        dates = []
        for m in months:
            dfs.append(self._df_expenses[self._df_expenses[month_col] == m])
            dates.append(datetime(year=m // 12, month=m%12+1, day=1))
        return dates, dfs
    
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
        #df = df[df[self._config["name_column"]] != self._config["name"]]
        return df.reset_index(drop=True)

    def get_week_count(self):
        df = self._df_expenses
        date_col = self._config["date_column"]
        date_f = self._config["date_format"]
        date_f = get_date_format(date_f)
        start = datetime.strptime(df[date_col][len(df)-1], date_f)
        stop = datetime.strptime(df[date_col][0], date_f)
        return (stop - start).days / 7