import sys
import os
from utils import add_up_expenses
from plot_utils import AdvancedPiePlot
from categorizer import Categorizer
import configparser
import argparse

parser = argparse.ArgumentParser(prog="Expense Total",
                                 description="Plot a pie chart of the categories of all your expenses.")
parser.add_argument("folder")
parser.add_argument("-c", "--categorize", action="store_true")
parser.add_argument("-d", "--depth", type=int, default=1,
                    help="Depth for sub-categories. Higher depth for more fine-grained categories.")


args = parser.parse_args()

config = configparser.ConfigParser()
config.read(os.path.join(args.folder, "config.ini"), encoding="utf-8")
config.read(os.path.join(args.folder, "config.ini"), encoding=config["categorizing"]["encoding"])
cat = Categorizer(args.folder, config["categorizing"], depth=args.depth)


df_expenses = cat._df_expenses
weeks = cat.get_week_count()

expenses, indices_not_found = cat.collect()

if args.categorize:
    indices = cat.complete(save=True)
    expenses, indices_not_found = cat.collect(expenses=expenses)

print(f"{len(indices_not_found)} entries not categorized")
#ignored = expenses["Ignored"]
#print(f"{ignored['total']:.2f}€ ignored ({ignored['total']/weeks:.2f}€ per week)")

categories, totals, labels = add_up_expenses(expenses)

plot = AdvancedPiePlot(expenses, weeks)
plot.plot(totals, categories)
plot.add_annotations()
plot.finalize()
