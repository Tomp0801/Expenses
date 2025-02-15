import configparser
import re
import numpy as np

def get_kw_args(file, section):
    config = configparser.ConfigParser()
    config.read(file)
    args = dict(config[section])
    # auto type conversion
    for k, v in args.items():
        if v=="True":
            args[k] = True
        if v=="False":
            args[k] = False
        try:
            args[k] = int(v)
        except:
            pass
    return args

def get_date_format(date_f):
    if date_f.lower()=="dmy":
        return "%d.%m.%Y"
    elif date_f.lower()=="ymd":
        return "%Y.%m.%d"
    elif date_f.lower()=="mdy":
        return "%m.%d.%Y"
    elif date_f.lower()=="ydm":
        return "%Y.%d.%m"
    else:
        return "%d.%m.%Y"

def find_keyword(keyword, strings):
    for s in strings:
        if re.search(keyword, str(s).replace(" ", ""), re.IGNORECASE):
            return True
    return False

def add_expense_to_category(all_cats, cat_name, amount, keyword):
    if not cat_name in all_cats.keys():
        all_cats[cat_name] = {"total": 0.0, "amounts":[], "labels":[]}
    all_cats[cat_name]["total"] += -amount
    all_cats[cat_name]["amounts"].append(-amount)
    all_cats[cat_name]["labels"].append(keyword)

def add_up_expenses(expenses):
    cats = []
    totals = []
    labels = []
    for key, val in expenses.items():
        if key != "Ignored":
            cats.append(key)
            totals.append(val["total"])
            labels.append(val["labels"])
    return cats, totals, labels

def condense_amounts(labels, amounts):
    condensed = {}
    for i, label in enumerate(labels):
        if not label in condensed:
            condensed[label] = 0
        condensed[label] += amounts[i]
    return list(condensed.keys()), list(condensed.values())

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'same') / w

def get_all_leaves(node):
    if isinstance(node, list):
        return node
    elif isinstance(node, dict):
        elements = []
        for k, els in node.items():
            for el in get_all_leaves(els):
                elements.append(el)
        return elements

def flatten_categories(categories, depth=1, prefix=None):
    flattened = {}
    for k, sub_categories in categories.items():
        if prefix is None:
            cat = k
        else:
            cat = f"{prefix}-{k}"
        if depth == 1 or isinstance(sub_categories, list):
            flattened[cat] = get_all_leaves(sub_categories)
        else:
            new_cats = flatten_categories(sub_categories, depth-1, prefix=cat)
            flattened.update(new_cats)
    return flattened