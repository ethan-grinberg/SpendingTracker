# Spending Tracker
It parses your transaction alert emails from Chase and aggregates your monthly transactions, so you can compare to your budget.
## How to Use
- Clone this repository
- pip install the dependencies
- set up your transaction alerts to go to a folder called `Transactions`
- change the email to your email in line 42 of `app.py`
- Add your bills to `budget.xlsx` in the  `bills` sheet and your budget to the `budget` sheet. Bills are considered reoccuring expenses.
- run `python app.py update <your password>` to read in all transactions since last updated
- run `python app.py all <your password>` to read all transactions in the transactions folder
- run `python app.py viz` to visualize your top expenses for the month so far, your month's expenses vs. your budget, and your budget breakdown for the month (pie chart)
- run `python app.py viz_all` to show your spending for the entire year and your expected spending for the entire year.
