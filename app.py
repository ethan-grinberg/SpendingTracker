import re
import imapclient
import pyzmail
import sys
import pandas as pd
import visualization
from datetime import datetime
import dateutil.parser

transaction_file = "transactions.xlsx"


def parse_chase_transaction(email, subject, is_credit, date):
    # get charge amount and get rid of dollar sign and convert to float
    charge_amount = extract('\$[\d,]*(\.\d{2})', email)
    charge_amount = charge_amount.replace("$", "")
    amount = float(charge_amount)

    # get description
    description_regex = '(?<=with\ )(.*)'
    description = ""
    if is_credit:
        # the description is in the subject if it's a credit transaction, unlike debit
        description = extract(description_regex, subject)
    else:
        description = extract(description_regex, email)
    # strip extra characters
    description = description.strip()

    data = (date, amount, description)
    return data


def extract(regex, body):
    result = re.search(regex, body)
    return "NOT FOUND" if result is None else result.group()


def get_recent_transactions(last_date, password):
    # Login to email
    imapObj = imapclient.IMAPClient('imap.gmail.com', ssl=True)
    imapObj.login('ethan.gsoccer26@gmail.com', password)

    # Look at transactions folder
    imapObj.select_folder('Transactions', readonly=True)

    # Find all transactions since specified date
    UIDs = imapObj.search(['SINCE', last_date])
    transactions = []
    for UID in UIDs:
        rawMessages = imapObj.fetch([UID], ['BODY[]', 'FLAGS'])
        message = pyzmail.PyzMessage.factory(rawMessages[UID][b'BODY[]'])
        decoded_message = message.text_part.get_payload().decode(message.text_part.charset)

        # get date of email
        date_raw = message.get_decoded_header("Date")
        dt = dateutil.parser.parse(date_raw)
        date = datetime(dt.year, dt.month, dt.day, 0, 0, 0)

        # credit transactions parsed slightly differently
        is_credit = False
        subject = message.get_subject()
        if 'debit' not in subject:
            is_credit = True
        transaction = parse_chase_transaction(decoded_message, subject, is_credit, date)

        # add data
        transactions.append(transaction)

    # logout of email
    imapObj.logout()

    return transactions


def add_new_transactions(all_transactions, password):
    # arbitrary date that is far before I even had a bank account
    last_date = datetime(2008, 1, 1, hour=0, minute=0, second=0)

    columns = ["date", "amount", "description"]

    # load in existing transactions and drop duplicates
    existing_transactions = pd.read_excel(transaction_file, sheet_name="transactions", usecols='A:C')

    # only get transactions since last updated
    if not all_transactions:
        last_date = existing_transactions.iloc[-1].date

    # get new transactions and combine with old ones
    new_transactions = pd.DataFrame(get_recent_transactions(last_date, password), columns=columns)
    all_transactions = pd.concat([existing_transactions, new_transactions])

    # get rid of duplicates and write to excel
    all_transactions.drop_duplicates(subset=columns, inplace=True)
    all_transactions.sort_values(by="date", inplace=True)
    all_transactions.to_excel(transaction_file, columns=columns, index=False, sheet_name="transactions")


update_transactions = sys.argv[1]
# main function from command line
if update_transactions == "update":
    add_new_transactions(False, sys.argv[2])
elif update_transactions == "all":
    add_new_transactions(True, sys.argv[2])
elif update_transactions == "viz":
    visualization.top_expenses()
    visualization.show_budget_and_expenses()
    visualization.show_budget_breakdown()
elif update_transactions == "viz_all":
    visualization.show_all_spending()
    visualization.show_future_spending()
else:
    print("invalid command")
