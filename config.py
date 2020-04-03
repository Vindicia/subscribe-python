# Configuration for Subscribe Python scripts
# Intended for import into python script/module
#

import os
import logging
import pytz
import argparse
from datetime import date, datetime
import json
import re
import socket

from utils import api_return, setup_custom_logger, randName

# Set the timezone to match CashBox
timezone = pytz.timezone('America/Los_Angeles')
# Current time converted to target time zone (set above) as string
here_now = datetime.now()
# Convert to defined timezone
there_now = here_now.astimezone(timezone)
# As string to use in class IDs
suffix = there_now.strftime('%Y%m%d:%H%M%S')

# Set global variables from environment
try:
    # HMAC_KEY = os.environ['hmac_key']
    # DEBUG = int(os.environ['debug'])
    # REGION_NAME = os.environ['regionName']
    # BUCKET_NAME = os.environ['s3Bucket']
    # API_CREDS = os.environ['api_key'].split(":")
    # VIN_VERSION = os.environ['vin_Version']
    # VINENV = os.environ['vinEnv']
    HMAC_KEY = 'hmav_key'
    DEBUG = 0
    REGION_NAME = 'us-east-1'
    BUCKET_NAME = 'none'
    API_CREDS = 'api_user:api_password'.split(":")
    VIN_VERSION = '23.0'
    VINENV = 'Prodtest'
    USERAGENT = socket.gethostname()+'-dev'
    RETRY_COUNT = 3
    nameJSON = 'mylib/CharacterNames.json'
    rest_host = 'api.prodtest.vindicia.com'
    LOG = 'logs/create.log'
    db = {
        "host": "db131.prodtest2.vindicia.com",
        "port": "5432",
        "database": "pgprodtestdb1",
        "user": "pg_user",
        "password": "pg_password",
        "schema": "pg_schema",
    }
except Exception:
    # No logger has been defined yet so print the traceback and return an error
    import traceback
    traceback.print_exc()
    api_return("400", "ERROR: Missing required environment >" + "<")

# Setup Logging - logging to stdout
log = setup_custom_logger('root')

# create a parser object
parser = argparse.ArgumentParser(description="Python wrapper for Subscribe")

# Applcation control
parser.add_argument("--debug", metavar="debug", type=int,
                    help="Integer debug level for this script",
                    default=0)
parser.add_argument("--nocreate", action='store_true',
                    help="If set, new Subscription creation will be skipped.")
parser.add_argument("--getdata", action='store_true',
                    help="If set, no database queries are perfomed to get transaction details for a Subscription.")

# Customer specific data
#
parser.add_argument("--accountid", metavar="<accountid>", type=str,
                    help="Merchant identifier for Account object",
                    default="vin-tst-acct-"+suffix)
parser.add_argument("--name",  metavar="<customer full name>", type=str,
                    help="The customer’s name, usually corresponding to name on credit card",
                    default=json.loads(randName()['body'])[0])
parser.add_argument("--addr1", metavar="<address line 1>", type=str,
                    help="First line of address. ",
                    default="1500 Marilla St")
parser.add_argument("--addr2", metavar="<address line 2>", type=str,
                    help="Second line of address")
parser.add_argument("--city", metavar="<city>", type=str,
                    help="Address city",
                    default="Dallas")
parser.add_argument("--district", metavar="<state/province>",
                    type=str, help="Address state/province",
                    default="TX")
parser.add_argument("--county", metavar="<county>", type=str,
                    help="Address county")
parser.add_argument("--country", metavar="<country>",
                    type=str, help="Address country",
                    default="US")
parser.add_argument("--postalcode", metavar="<postalCode>", type=str,
                    help="Customer zip/postal code",
                    default="75201")
parser.add_argument("--phone", metavar="<phone>", type=str,
                    help="Customer phone number",
                    default="555-214-1212")
parser.add_argument("--defaultcurrency", metavar="<code>", type=str,
                    help="ISO 4217 currency code to use for this operation",
                    default="USD")
parser.add_argument("--preferredlanguage", metavar="<code>", type=str,
                    help="W3C IANA Language Subtag Registry code for customer preferred language",
                    default="EN")
parser.add_argument("--email", metavar="<email>", type=str,
                    help="Customer email address",
                    default='ttucker@vindicia.com')
parser.add_argument("--emailtypepreference", type=str,
                    choices=['html', 'plaintext'],
                    help="Customer preferred format for email messages",
                    default="html")
parser.add_argument("--externalid", metavar="<externalId>", type=str,
                    help="Merchant additional unique identifier for this "
                    "Account. Uniqueness or null for this value is "
                    "enforced by Subscribe per Merchant")
# parser.add_argument("--ssn", metavar="<ssn>", type=str,
#                     help="Customer social security number. This value will be " \
#                     "stored encrypted in CashBox and is not returned by CashBox")


# Payment related arguments
parser.add_argument("--paymentid", metavar="<paymentid>", type=str,
                    help="Merchant identifier for PaymentMethod object",
                    default="vin-tst-pm-"+suffix)
parser.add_argument("--creditcard", nargs=1,
                    metavar="creditcard", type=int,
                    help="Credit card account number",
                    default="4485983356242217")
parser.add_argument("--expirationdate", metavar="<YYYYMM>", type=str,
                    help="4 Digit year and 2 digit month of credit card "
                    "expiration date (YYYYMM). Defaults to 1 year from today",
                    default=there_now.replace(year=there_now.year + 1).strftime('%Y%m'))
parser.add_argument('--cvn', metavar="cvn", type=str,
                    help="Card Verification Number",
                    default="300")
parser.add_argument("--map", action='store_true',
                    help="Flag to trigger use of MerchantAcceptedPayment "
                    "payment method for purchase")
parser.add_argument("--paypal", action='store_true',
                    help="Flag to trigger PayPal PaymentMethod for CashBox "
                    "operation")
parser.add_argument("--paypalnoshippingaddress",  action='store_true',
                    help="Flag to trigger masking of the PayPal shipping "
                    "address for customers buying digital goods.")
parser.add_argument('--paypalcancel', metavar='<url>',
                    help="URL to which to redirect if PayPal indicates failure "
                    "after completeing payment process on PayPal site",
                    default='http://localhost/paypalcancel.php')
parser.add_argument('--paypalreturn',  metavar='<url>',
                    help="URL to which to redirect after successfully "
                    "completeing payment transactions on PayPal site",
                    default='http://localhost/paypalcancel.php')

# Subscription related arguments
parser.add_argument("--autobillid", metavar="<autobillid>", type=str,
                    help="Merchant identifier for AutoBill object",
                    default="vin-tst-ab-"+suffix)
parser.add_argument("--starttimestamp", nargs=1,
                    metavar="<YYYY-MM-DDTHH:MM:SS>",
                    # type=lambda d: str(datetime.strftime(datetime.strptime(d, '%Y-%m-%dT%H:%M:%S'), '%Y-%m-%dT%H:%M:%S'),
                    type=lambda d: datetime.strptime(d, '%Y-%m-%dT%H:%M:%S'),
                    help="A time stamp that specifies the start date and "
                    "time for this AutoBill object. If unspecified, "
                    "the value defaults to today and the current time.",
                    default=there_now) #.strftime('%Y-%m-%dT%H:%M:%S'))
# parser.add_argument("--statementoffset", metavar="n", type=int,
#                     help="Days prior to billing that a statement will be sent. "
#                     "This value must be \"null\" or \"0\" if the AutoBill "
#                     "PaymentMethodType is MerchantAcceptedPayment. For "
#                     "conventionally-funded AutoBills, this value must be "
#                     "less than the prebilling notification days (if "
#                     "specified). The value will be ignored if "
#                     "statementFormat is DoNotSend.")
parser.add_argument("--invoiceterms", metavar="n", type=int,
                    help="The number of days after the invoice date that a "
                    "bill is considered delinquent, if the AutoBill "
                    "payment method is MerchantAcceptedPayment. This "
                    "value will be ignored for all other payment methods.")
parser.add_argument("--specifiedbillingday", metavar="n", type=int,
                    help="Integer (1-31) specifying the day of the month on "
                    "which to bill (values 29-31 automatically work as the "
                    "last day of the month for calendar months that do not "
                    "have 29, 30, or 31 days). Providing no value or null "
                    "in this parameter instructs CashBox to bill on the "
                    "service period start date (the default)")
parser.add_argument("--billingrule", choices=['Advance', 'Arrears'],
                    metavar="<billingrule>", type=str,
                    help="An enumerated string value (Advance or Arrears), "
                    "informing CashBox in which direction from the "
                    "scheduled billing date to select the specified "
                    "billing date. If no specified_billing_day is "
                    "provided, this parameter is ignored.")
# parser.add_argument("--billingoffset", metavar="n", type=int,
#                     help="billingOffset")


# BillingPlan arguments
parser.add_argument("--billingplanid", metavar="<merchantBillingplanId>", type=str,
                    help="Merchant identifier for BillingPlan object",
                    default="Monthly")

# Subscription item arguments
parser.add_argument("--productid", nargs='*', metavar="<productid>", type=str,
                    help="One or more CashBox Product object identifiers for "
                    "items of the subscription",
                    default="SUB04")
parser.add_argument("--cycles", metavar="n", type=str,
                    help="The number of billing cycles this item will be active")

# parser.add_argument("--amount", metavar="amount",
#                     type=str, help="amount")

# Run time elements
parser.add_argument("--transactionid", metavar="<merchantTransactionId>",
                    type=str,
                    help="Merchant unique identifier for a CashBox Transaction object")

parser.add_argument("--taxclassification", nargs='*',
                    metavar="<taxClassification>", type=str,
                    help="Tax classification override, appropriate for tax engine, for this item(s). "
                    "Applied positionally to individual items")


# parser.add_argument("--child", metavar="child",

# parser.add_argument("--hoamethod", nargs=1,
# metavar="hoamethod", type=str, help=" ", default=" ")
parser.add_argument("--itemsku", nargs='*', metavar="sku", type=str,
                    help="Product identifier(s) for item(s). Only "
                    "used in context of one-time transactions")
parser.add_argument("--itemname", nargs='*', metavar="itemname", type=str,
                    help="Product name(s) for item(s). Only used in context "
                    "of one-time transactions")
parser.add_argument("--itemprice", nargs='*', metavar="<itemprice>", type=float,
                    help="Price(s) to be applied positionally to individual items")
parser.add_argument("--itemqty", nargs='*', metavar="itemqty",
                    type=int, help="Product quantity(ies) for item(s)")
parser.add_argument("--itemstartdate", nargs='*', metavar="<YYYY-MM-DD>", type=str,
                    help="Start date to be used for AutoBill. Defaults to script runtime")
parser.add_argument("--itemcampaign", nargs='*', metavar="<campaigCode>", type=str,
                    help="Campaign code(s) to be applied positionally to individual items")
parser.add_argument("--itemcycles", nargs='*', metavar="n", type=int,
                    help="Fixed count of billing cycles to be used for item(s). Applied positionally to individual items",)


# parser.add_argument("--note", metavar="note",
#                     type=str, help=" ", default=" ")
# parser.add_argument("--parent", metavar="parent",
#                     type=str, help=" ", default=" ")
# parser.add_argument("--payerreplacementbehavior", nargs=1,
#                     metavar="payerreplacementbehavior", type=str, help=" ", default=" ")
# parser.add_argument("--paymenttype", nargs=1,
#                     metavar="paymenttype", type=str, help=" ", default=" ")


# Method parameters
parser.add_argument("--srd", metavar="<srd>",
                    type=str,
                    help="Sparse Response Description, a SOAP string (which "
                    "must be a JSON object), specifying the CashBox data "
                    "elements to be returned by the operation",
                    default='')
parser.add_argument("--cancelreason", metavar="cancelreason", type=int,
                    help="Integer reason code for canceling the AutoBill")
parser.add_argument("--campaigncode", metavar="<campaignCode>", type=str,
                    help="String Coupon or Promotion code, from CashBox "
                    "Campaign, to apply discount on this AutoBill")
parser.add_argument("--dryrun", action='store_true',
                    help="Flag that, if set, will return updated AutoBill, "
                    "without recording the result in the CashBox database")
parser.add_argument("--replaceonallautobills", action='store_true',
                    help="Flag that, if set, causes the update of a payment "
                    "method to propagate to all the AutoBill objects "
                    "associated with the Account object")
parser.add_argument("--replaceonallchildautobills", action='store_true',
                    help="Flag that, if set, causes the update of a payment "
                    "method to propagate to all the AutoBill objects "
                    "associated with child Accounts of the Account object")
parser.add_argument("--sendemailnotification", action='store_true',
                    help="Flag that, if set, triggers email notification "
                    "from CashBox for one-time Transaction operations")
parser.add_argument("--force", action='store_true',
                    help="Flag that cancels the subscription even "
                    "if the minimum commitment period for this AutoBill "
                    "object has not been satisfied")
parser.add_argument("--ignoreavspolicy", action='store_true',
                    help="Flag triggering override of AVS policy to "
                    "accept the payment method, regardless of the "
                    "AVS return code from the processor")
parser.add_argument("--ignorecvnpolicy", action='store_true',
                    help="Flag triggering override of CVN policy to "
                    "accept the payment method, regardless of the "
                    "CVN return code from the processor")
parser.add_argument("--immediateauthfailurepolicy", type=str,
                    choices=['doNotSaveAutoBill', 'putAutoBillInRetryCycle',
                             'putAutoBillInRetryCycleIfPaymentMethodIsValid'],
                    help="Enumerated string for behavior if payment method fails validation",
                    default='doNotSaveAutoBill')
parser.add_argument("--initialauth", type=str,
                    choices=['AuthImminentBilling',
                             'DelayFullAuthToInitialBillingDate'],
                    help="Enumerated string specifying how to manage "
                    "authorization and capture when scheduled initial "
                    "billing is within 25 hours",
                    default='AuthImminentBilling')
parser.add_argument("--minchargebackprobability", metavar="n", type=int,
                    help="Integer between 0 and 100 identifying fraud risk tolerance level",
                    default='100')
parser.add_argument("--validateforfuturepayment", action='store_true',
                    help="Integer boolean. If true and billing scheduled for "
                    "future date, triggers minimal authorization ($0/$1) immediately")

# Account.updatePaymentMethod unique parameters
# parser.add_argument("--updatebehavior", nargs=1,
#                     metavar="updatebehavior", type=str, help=" ", default=" ")
# parser.add_argument("--updatescopeonchildren", nargs=1,
#                     metavar="updatescopeonchildren", type=str, help=" ", default=" ")
# parser.add_argument("--validatepaymentmethod", nargs=1,
#                     metavar="validatepaymentmethod", type=str, help=" ", default=" ")
# parser.add_argument("--updatescopeonaccount", type=str,
#                     choices=['None', 'matchingPaymentMethod',
#                              'AllDue', 'AllDueAndMatching', 'AllActive'],
#                     help="Enumerated string controlling whether and when to "
#                     "bill and/or replace the paymentMethod on associated "
#                     "AutoBills belonging to the specified Account.", default="None")

# parse the arguments from standard input
args = parser.parse_args()

# Need dryrun set to integer true or false so no errors when it is used
if args.dryrun:
    args.dryrun = 1
else:
    args.dryrun=0

# logger.debug("defaults: %s", json.dumps(vars(args), indent=4))

   
# Make sure starttimestamp is an ISO 8601 string
#
# For some reason argparse makes this a list unless it defaults
# Likely ID10T error
if (type(args.starttimestamp) is list):
    # Before we muck with with it, lets reset suffix
    old_suffix = suffix
    suffix = args.starttimestamp[0].strftime('%Y%m%d:%H%M%S')
    if (re.search(old_suffix, args.accountid)):
        args.accountid = f'vin-rest-acct-{suffix}'
    if (re.search(old_suffix, args.autobillid)):
        args.autobillid = f'vin-rest-ab-{suffix}'
    if (re.search(old_suffix, args.paymentid)):
        args.paymentid = f'vin-rest-pm-{suffix}'
    args.starttimestamp = args.starttimestamp[0].astimezone(
        timezone).isoformat()
elif (type(args.starttimestamp) is datetime):
    args.starttimestamp = args.starttimestamp.isoformat()

# Make sure expirationdate is a date and format to "YYYYMM"
if args.expirationdate:
    try:
        expirationdate = datetime.strptime(
            args.expirationdate, '%Y%m').strftime('%Y%m')
        args.expirationdate = expirationdate
    except Exception:
        log.error('Invalid --expirationdate >%s<. Defaulting',
                     args.expirationdate)
        args.expirationdate = there_now.replace(
            year=there_now.year + 1).strftime('%Y%m')
