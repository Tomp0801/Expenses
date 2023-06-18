from inout import read_all_expenses, read_categories, ask_choice
from utils import get_kw_args, read_expenses, lower_no_space, find_keyword, collect_expenses
import json
import numpy as np

class Categorizer:
    def __init__(self, folder, date_column, delimiter=',', encoding="utf-8",
                 categories_file="categories.json",
                 outgoing=True, incoming=False) -> None:
        self._df = read_all_expenses(folder, date_column=date_column, 
                                     delimiter=delimiter, encoding=encoding)
        self._categories_file = categories_file
        self._categories = read_categories(categories_file)
        self._expenses_df = read_expenses(self._df, negative=outgoing, positive=incoming)

        
    @staticmethod
    def create(folder, config_file):
        return Categorizer(folder, **get_kw_args(config_file, "categorizing"))
    
    def complete(self, save=True):
        expenses, indices_not_found = collect_expenses(self._df_expenses, self._categories)

        indices = self.categorize(indices_not_found, save_categories=save)
        missing_expenses = self._df_expenses[indices]

        
    def categorize(self, indices, categories, save_categories=True):
        categorized_indices = []
        for i in indices:
            amount = self._expenses_df.loc[i, "Betrag"]
            sender = self._expenses_df.loc[i, "Verwendungszweck"]
            purpose = self._expenses_df.loc[i, "Auftraggeber/Empfänger"]
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