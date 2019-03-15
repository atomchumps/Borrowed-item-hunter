#!/usr/bin/python

'''
A program for monitoring borrowed lab equiptment and requesting returns
A. J. McCulloch, March 2019
'''

####################################################################################################
# Import modules
####################################################################################################

import pandas as pd # Used for dataframes
import numpy as np # Used more maths
import getpass # Hides inputs when entering passwords
import schedule # Required for scheduling
import time # Used for program time management
from datetime import * #Used for calculations involving time

####################################################################################################
# Define functions
####################################################################################################

# Function to send an email
def send_email(user, pwd, recipient, subject, body):
    import smtplib

    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Establish a connection with Gmail
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
    except:
        print("Connection to Gmail failed, check netowrk connection")

    # Login to Gmail
    try:
        server.login(user, pwd)
    except:
        print("Gmail login failed. Check password or security settings")

    # Send the message
    try:
        server.sendmail(FROM, TO, message)
        server.close()
        print("Mail successfully sent to {}".format(recipient))
    except:
        print("Mail sending failed")

# Function to return a dataframe of borrowed items, input is web address of .csv file containing borrwed items info
def csvtodf(csv_loc):
    # Create a dataframe from the data stored in the spreadsheet link
    df = pd.read_csv(link, encoding = 'utf8')
    # Create a variable from the row containing headers
    headers = df.iloc[0]
    # Replace the dataframe removing the headers row
    df = df[1:]
    # Rename the dataframe's column values with the headers
    df.columns = headers
    # Convert timestamp to datetime object
    df['Timestamp'] = df['Timestamp'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y %H:%M:%S'))
    # Convert timestamp to datetime object
    df['Estimated return date'] = df['Estimated return date'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y'))
    # Calculate the length of the current loan
    df['Current loan length'] = (datetime.today() - df['Timestamp']).dt.days
    # Calculate estimated loan length
    df['Estimated length of loan'] = (df['Estimated return date']-df['Timestamp']).dt.days

    return df

# Return the overdue items in a dataframe (must be created via csvtodf)
def findoverdue(df):
    return df[df['Current loan length'] > df['Estimated length of loan']]

# Generate the body of the email to send requesting equiptment return
def makebody(content):
    body = "Dear {},\n\nYou are receiving this message as you are receiving this \
message as you borrowed some equipment from the optics group on {:%B, %d %Y}.\n\n\
The item(s) listed as borrowed are {}. \n\nAs it stands, you estimated \
that you would need the item(s) for {} days but you have had them for \
{} days. Please return the items to the lab (560) or contact someone from \
the lab to discuss extending the borrowing period. As a reminder, the \
initial loan was authorised by {}. \n\nNote that this email address is not \
monitored, so do not reply to this address.\n\nThanks and kind regards,\n\n\
Room 560".format(content['Name'], content['Timestamp'], content['Item(s)'], content['Estimated length of loan'], content['Current loan length'], content['Authorisation'])

    return body

# Function to look for overdue items and email the thieves
def spam():
    # Create a dataframe of overdue items
    overdue = findoverdue(csvtodf(csvloc))
    # Iterate over the overdue items and send return request emails
    for rows in overdue.iterrows():
        # Make a dictionary of the conent of each overdue item
        # First element of the iterable is the index, hence taking the second
        content_dict = rows[1].to_dict()
        # Generate the body of the email requesting return
        bodytext = makebody(content_dict)
        # Send the reminder email
        send_email(emailfrom, pwd, content_dict['Email address'], subject, bodytext)

####################################################################################################
# Program parameters
####################################################################################################

# Email address from which return reminders will be sent
emailfrom = 'atomchumps@gmail.com'
# Subject line for email requesting the return of equiptment
subject = "Overdue equiptment"
# Define the link where the borrowed items register is stored
csvloc = r'https://docs.google.com/spreadsheets/d/e/2PACX-1vRR-Oy5K6At38q_3KvZWzUIBeIkTVn-_lE3RTDy0ieuvoN6gk1qh6hoSSRLdTZuyJmexJ43bj62ScAx/pub?gid=465314900&single=true&output=csv'

####################################################################################################
# Actual program
####################################################################################################
# This needs to be run as a background process
# eg "nohup python hunter.py &" on a Linux machine

# Get the atomchumps password, required for sending emails
pwd = getpass.getpass("Enter the password for atomchumps:")

# Schedule a run every Monday morning at 0800
schedule.every().monday.at("08:00").do(spam)

while True:
    schedule.run_pending()
    time.sleep(1) # wait one second
