import sys
import json
from inout import categorize, read_categories, read_expense_file
from utils import get_week_count, read_expenses, collect_expenses, add_up_expenses
from plot_utils import AdvancedPiePlot

dont_ask = False

file = sys.argv[1]
categories = read_categories()
input_df = read_expense_file(file, date_column="Buchung", delimiter=";", encoding="cp1252")
df_expenses = read_expenses(input_df, only_negative=True)

weeks = get_week_count(df_expenses)

expenses, indices_not_found = collect_expenses(df_expenses, categories)

if not dont_ask:
    indices = categorize(df_expenses, indices_not_found, categories, save_categories=True)
    missing_expenses = df_expenses[indices]
    expenses, indices_not_found = collect_expenses(df_expenses, categories, expenses=expenses)

print(f"{len(indices_not_found)} entries not categorized")
ignored = expenses["Ignored"]
print(f"{ignored['total']:.2f}€ ignored ({ignored['total']/weeks:.2f}€ per week)")

categories, totals, labels = add_up_expenses(expenses)

plot = AdvancedPiePlot(expenses, weeks)
plot.plot(totals, categories)
plot.add_annotations()
plot.finalize()
