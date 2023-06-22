import numpy as np
import sys
from plot_utils import AdvancedLinePlot
from categorizer import Categorizer
import configparser

dont_ask = True
top = 6

ignore = [
    #"Wohnung", 
    "Urlaub"
    ]

file = sys.argv[1]
config_file = sys.argv[2]

config = configparser.ConfigParser()
config.read(config_file)
cat = Categorizer(file, config["categorizing"])

df_expenses = cat._df_expenses
weeks = cat.get_week_count()

expenses, indices_not_found = cat.collect()

if not dont_ask:
    indices = cat.complete(save=True)
    expenses, indices_not_found = cat.collect(expenses=expenses)

dates, dfs = cat.divide_by_months()

plot = AdvancedLinePlot()
totals = {}

for i, df in enumerate(dfs):
    expenses, _ = cat.collect(df, expenses={})
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