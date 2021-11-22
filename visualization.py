import pandas as pd
from datetime import date
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# budget file
budget_file = "budget.xlsx"
transaction_file = "transactions.xlsx"

# global variable for the number of most expensive transactions to display
top_transactions_num = 12

# get all transactions
transactions = pd.read_excel(transaction_file, sheet_name="transactions")

# gets this months transactions
today = date.today()
start_month = datetime(today.year, today.month, 1)
months_transactions = transactions.loc[transactions.date >= start_month]

# global figsize
figsize = (10, 5)


def load_bills():
    # load in bills and convert to datetime
    bills = pd.read_excel(budget_file, sheet_name="bills")
    bills["date"] = pd.to_datetime(bills.date)

    # get current month's bills
    bills['month'] = bills.date.dt.month.to_list()
    return bills


def load_budget():
    return pd.read_excel(budget_file, sheet_name="budget")


def add_budget_and_bills():
    bills = load_bills()
    budget = load_budget()

    bills = bills.loc[bills.month == today.month]
    bills = bills.loc[:, ["description", "amount"]]

    return pd.concat([budget, bills])


def top_expenses():
    top_transactions = months_transactions.groupby("description").amount.sum()
    top_transactions.sort_values(inplace=True, ascending=False)

    if len(top_transactions) >= top_transactions_num:
        top_transactions = top_transactions.iloc[:top_transactions_num]

    plt.figure(figsize=figsize)
    # plot top expenses
    bars = plt.bar(top_transactions.index.to_list(), top_transactions.to_list())

    # add bar labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + .2, yval)

    plt.title("top expenses")
    plt.show()


# get budget
final_budget = add_budget_and_bills()


def show_budget_and_expenses():
    data = [months_transactions.amount.sum(), final_budget.amount.sum()]

    plt.figure(figsize=figsize)
    bars = plt.bar(["expenses", "budget"], data)

    # add bar labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + .2, yval)

    plt.title("budget vs. expenses")
    plt.show()


def show_budget_breakdown():
    fig = plt.figure(figsize=figsize)
    plt.pie(final_budget.amount, labels=final_budget.description, autopct='%.1f%%')

    plt.title("this month's budget breakdown")
    plt.show()


def show_all_spending():
    fig = plt.figure(figsize=figsize)
    this_year_transactions = transactions.loc[transactions.date > datetime(today.year, 1, 1)]

    this_year_transactions["month"] = this_year_transactions.date.dt.month.to_list()

    data = this_year_transactions.groupby("month").amount.sum()
    bars = plt.bar(data.index.to_list(), data.to_list())

    # add bar labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + .2, yval)

    plt.title("this year's spending")
    plt.show()


def show_future_spending():
    monthly_budget = load_budget()
    monthly_budget = monthly_budget.amount.sum()
    bills = load_bills()

    # group bills and add budget to each month
    monthly_bills = bills.groupby("month").amount.sum()

    # all months to fill data
    months = pd.Series(np.zeros(12), index=np.arange(1, 13), name="months")
    monthly_bills = pd.merge(monthly_bills, months, left_index=True, right_index=True, how='right')
    monthly_bills = monthly_bills.fillna(0).amount

    # combine future all bills with monthly budget
    predicted_spending = monthly_bills + monthly_budget

    # plotting
    fig = plt.figure(figsize=figsize)
    bars = plt.bar(predicted_spending.index, predicted_spending)

    # add bar labels
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x(), yval + .2, yval)

    # add lines to bars
    axes2 = plt.twinx()
    axes2.plot(predicted_spending.index, predicted_spending, color='k', label='future_spending')

    plt.title("predicted yearly spending")
    plt.show()




