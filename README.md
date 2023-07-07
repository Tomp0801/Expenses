# Expenses
Visualize your expenses read from a csv file

## Setup
- Setup a virtual environment, activate it and install the required packages:
```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```
- Create a subdirectory beginning with `data_` (directory will be ignored by git)
- Edit the config.ini file to match your .csv files (you can copy it into your data directory)
- Copy your expenses csv files into your data directory. Get them from your online banking portal for example.

## Usage
You need to categorize your expenses. Do this by running a programm with the -c option. The file `categories.json` will be created which you can also manually edit.

### Total expenses
```bash
python ExpenseTotal.py -h
```

### Expense over time
```bash
python ExpenseTrend.py -h
```
