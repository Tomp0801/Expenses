import numpy as np
import sys
from inout import read_categories, read_all_expenses
from utils import read_expenses, divide_df, collect_expenses
from plot_utils import AdvancedLinePlot

top = 6

ignore = [
    #"Wohnung", 
    "Urlaub"
    ]

file = sys.argv[1]
categories = read_categories()
input_df = read_all_expenses(".", date_column="Buchung", delimiter=";", encoding="cp1252")
expenses_df = read_expenses(input_df, only_negative=True)

dates, dfs = divide_df(expenses_df)

plot = AdvancedLinePlot()
totals = {}

for i, df in enumerate(dfs):
    expenses, _ = collect_expenses(df, categories, expenses={})
    for category in expenses.keys():
        if category=="Ignored" or category in ignore:
            continue
        if not category in totals:
            totals[category] = [0] * len(dfs)
        totals[category][i] = (expenses[category]["total"])

sums = []
cats = []
tots = []
for cat, tot in totals.items():
    sums.append(np.sum(tot))
    cats.append(cat)
    tots.append(tot)

plot_tots = []
plot_labels = []
for i in range(top):
    ind = np.argmax(sums)
    sums[ind] = -1
    plot_tots.append(tots[ind])
    plot_labels.append(cats[ind])
#    plot.plot(dates, tots[ind], label=cats[ind])

# add other
other = np.zeros(len(plot_tots[0]))
for i in range(len(sums)):
    if sums[i] > 0:
        other = other + np.array(tots[i])

plot_tots.append(other)
plot_labels.append("Other")

plot.stackplot(dates, plot_tots, plot_labels)

plot.finalize()