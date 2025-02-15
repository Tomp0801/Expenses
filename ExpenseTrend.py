import numpy as np
import os
from analysis.plot_utils import AdvancedLinePlot
from categorizing.categorizer import Categorizer
import configparser
import argparse
from categorizing.utils import moving_average

parser = argparse.ArgumentParser(prog="Expense Trend",
                                 description="Plot your expenses over the course of months.")
parser.add_argument("folder", 
                    help="Folder in which csv files with expenses are stored. \
                        Must also contain a config.ini file with parameters for reading the csv files.")
parser.add_argument("-c", "--categorize", action="store_true", 
                    help="With this option, the program will ask you to categorize uncategorized items, otherwise they will be ignored.")
parser.add_argument("-m", "--max-categories", type=int, default=None,
                    help="Maximum number of categories to plot. The categories with most expenses will be chosen.")
parser.add_argument("-o", "--plot-other", action="store_true")
parser.add_argument("-e", "--exclude", nargs="+", default=[])
parser.add_argument("-i", "--include", nargs="+", default=[])
parser.add_argument("-s", "--smoothen", type=int, default=None,
                    help="Smoothen the results when plotting over a window with the given size.")
parser.add_argument("-d", "--depth", type=int, default=1,
                    help="Depth for sub-categories. Higher depth for more fine-grained categories.")


args = parser.parse_args()

top = args.max_categories

config = configparser.ConfigParser()
config.read(os.path.join(args.folder, "config.ini"), encoding="utf-8")
config.read(os.path.join(args.folder, "config.ini"), encoding=config["categorizing"]["encoding"])
cat = Categorizer(args.folder, config["categorizing"], args.depth)

df_expenses = cat._df_expenses
weeks = cat.get_week_count()

expenses, indices_not_found = cat.collect()

if args.categorize:
    indices = cat.complete(save=True)
    expenses, indices_not_found = cat.collect(expenses=expenses)

print(f"{len(indices_not_found)} entries not categorized")


dates, dfs = cat.divide_by_months()

plot = AdvancedLinePlot()
totals = {}

for i, df in enumerate(dfs):
    expenses, _ = cat.collect(df, expenses={})
    for category in expenses.keys():
        if len(args.include) > 0 and not category in args.include:
            continue
        if category=="Ignored" or category in args.exclude:
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
if top is None:
    top = len(sums)
top = min(top, len(sums))
for i in range(top):
    ind = np.argmax(sums)
    sums[ind] = -1
    plot_tots.append(tots[ind])
    plot_labels.append(cats[ind])
#    plot.plot(dates, tots[ind], label=cats[ind])

# add other
if args.plot_other:
    other = np.zeros(len(plot_tots[0]))
    for i in range(len(sums)):
        if sums[i] > 0:
            other = other + np.array(tots[i])
    plot_tots.append(other)
    plot_labels.append("Other")

if args.smoothen:
    plot_tots = [moving_average(pt, args.smoothen) for pt in plot_tots]

plot.stackplot(dates, plot_tots, plot_labels)

plot.finalize()