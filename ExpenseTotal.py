import sys
import json
from inout import read_categories, read_expense_file
from utils import get_week_count, read_expenses, collect_expenses, add_up_expenses
from plot_utils import AdvancedPiePlot
from categorizer import Categorizer
import configparser

dont_ask = True

file = sys.argv[1]
config_file = sys.argv[2]

config = configparser.ConfigParser()
config.read(config_file)
cat = Categorizer(file, config["categorizing"])
cat.complete()

df_expenses = cat._df_expenses
weeks = cat.get_week_count()


expenses, indices_not_found = cat.collect()

if not dont_ask:
    indices = categorize(df_expenses, indices_not_found, categories, save_categories=True)
    missing_expenses = df_expenses[indices]
    expenses, indices_not_found = collect_expenses(df_expenses, categories, expenses=expenses)

print(f"{len(indices_not_found)} entries not categorized")
#ignored = expenses["Ignored"]
#print(f"{ignored['total']:.2f}€ ignored ({ignored['total']/weeks:.2f}€ per week)")

categories, totals, labels = add_up_expenses(expenses)

plot = AdvancedPiePlot(expenses, weeks)
plot.plot(totals, categories)
plot.add_annotations()
plot.finalize()
