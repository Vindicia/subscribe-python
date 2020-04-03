#!/usr/bin/env python
# Create test data for documenting Gannet MAP invoice modifications

# Arguments:
#     Way too many to list here. Use -h to get list

# Returns:
#     null
#

import json
import logging
import os
from datetime import date, datetime, timedelta
import pytz
import decimal
import time
import requests
import csv
from operator import itemgetter
import psycopg2

from mylib.utils import *
import newAutoBill
import dbSQL

def main():
    response = create()
    config.log.info('Created %s', response['id'])

def create():
    """Create new Subscription

    Arguments:
        None

    Returns:
        response - dict - Subscribe API return for Subscription create or AutoBill.update
    """

    address = {
        'name': config.args.name,
        'line1': config.args.addr1,
        'city': config.args.city,
        'district': config.args.district,
        'postal_code': config.args.postalcode,
        'country': config.args.country,
        'phone': config.args.phone
    }

    account = {
        'id': config.args.accountid,
        'default_currency': config.args.defaultcurrency,
        'email': config.args.email,
        'email_type': config.args.emailtypepreference,
        'language': config.args.preferredlanguage,
        'name': config.args.name,
        'shipping_address': address,
        'metadata': {
            'account_metadata': 'metadata_value'
        }
    }
    billing_plan = {
        'id': config.args.billingplanid
    }

    payment_method = {
        'id': config.args.paymentid,
        'account_holder': config.args.name,
        'billing_address': {
            'name': config.args.name,
            'line1': config.args.addr1,
            'city': config.args.city,
            'district': config.args.district,
            'postal_code': config.args.postalcode,
            'country': config.args.country,
            'phone': config.args.phone
        }
    }
    if config.args.map:
        payment_method['type'] = 'MerchantAcceptedPayment'
        payment_method['merchant_accepted_payment'] = {
            'account': config.args.phone,
            'currency': config.args.defaultcurrency,
            'payment_type': 'Merchant Accepted Payment'
        }

    elif config.args.paypal:
        payment_method['type'] = 'PayPal'
        payment_method['paypal'] = {
            'returnUrl': config.args.paypalreturn,
            'cancelUrl': config.args.paypalcancel
        }
    else:
        # Put credit card  data into PaymentMethod object
        payment_method['type'] = 'CreditCard'
        payment_method['credit_card'] = {
            'account': str(config.args.creditcard),
            'expiration_date': config.args.expirationdate
        }
        # Set the CVN name/value for this PaymentMethod
        payment_method['metadata'] = {
            'CVN': config.args.cvn
        }

    items = [
        {
            'id': f'{config.args.autobillid}.001',
            'product': {
                'id': config.args.productid
            }
        }
    ]

    subscription = {
        'id': config.args.autobillid,
        'account': account,
        'billing_plan': billing_plan,
        'payment_method': payment_method,
        'currency': config.args.defaultcurrency,
        'description': config.args.autobillid,
        'items': items,
        'source_ip': '192.168.1.1',
        'notify_on_transition': False,
        'metadata': {
            'subscription_metadata': 'metadata_value'
        },
        'starts': config.args.starttimestamp,
        'policy': {
            'ignore_cvn_policy': False,
            'ignore_avs_policy': False,
            'min_chargeback_probability': 100,
            'immediate_auth_failure_policy': 'doNotSaveAutoBill'
        }
    }

    # if (type(subscription['starts']) is list):
    #     subscription['starts'] = subscription['starts'][0].astimezone(
    #         config.timezone).isoformat()
    # elif (type(subscription['starts']) is datetime):
    #     subscription['starts'] = subscription['starts'].isoformat()

    # config.log.debug(json.dumps(subscription, indent=4, default=json_serial))
    config.log.info('Create Subscription >%s< starts on >%s<', subscription['id'], subscription['starts'])
    if (config.args.dryrun):
        config.log.warning('--dryrun present so nothing will be saved. Hope that is expected')

    # Debugging short circuit around Subscription create for SQL testing
    # response = {
    #     'id': 'vin-rest-ab-20200331:130325'
    # }
    response = newAutoBill.newAutoBill(subscription)
    config.log.debug(json.dumps(response, indent=4, default=json_serial))
    config.log.info('Created Subscription >%s<', response['id'])
    return response

def db_getdbdata(ab_id: str):
    """Query database for transaction, transaction_billing and
        transaction_billing_item data for a specific Subscription.id or
        AutoBill.merchantAutoBillId.
    
        Outputs returned rows in CSV to file using merchant autobill identifier

        Arguments
            id {str} - Merchant identifier for Subscription/AutoBill
        
        Return
            null - Writes data to file name <autobill_identifier>.csv in current directory
    """

    # Connect to the database
    try:
        conn = dbconnect()
    except Exception:
        config.log.exception('Database connection failed')
        raise sys.exc_info()[0]

    # Using Subscription.id, get the database autobill.id
    sql = f'select id, product_serial from autobill ab where product_serial = \'{ab_id}\''
    config.log.debug(sql)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        autobills = cur.fetchall()
        config.log.info('%s rows returned from autobill table', len(autobills))
        if (len(autobills) < 1):
            config.log.warning('No autobill matching >%s< found in database', ab_id)
            return
    except Exception:
        config.log.exception('SELECT failed')
        raise sys.exc_info()[0]

    # Don't expect to receive more than 1 row, but you never know
    for autobill in autobills:
        config.log.info(f'Processing >{autobill[0]} for {ab_id}')
        # print(json.dumps(autobill, default=json_serial, indent=4))

        # Get the transaction_billings for an AutoBill by database id
        sql = f'select \
tb.id , \
autobill_id , \
merchant_txb_identifier , \
service_period_start_date , \
service_period_end_date, \
autobill_sequence , \
balance , \
grand_total , \
subtotal , \
sales_tax , \
bp_seq, \
tbs.status , \
next_activity , \
original_activity \
from transaction_billing tb \
join transaction_billing_status tbs on tbs.id = tb.cur_transaction_bill_status_id \
where autobill_id in ({autobill[0]}) \
order by autobill_id asc, autobill_sequence asc'

        copy = f'COPY ({sql}) TO STDOUT WITH CSV HEADER FORCE QUOTE *'
        try:
            config.log.info(f'Getting transaction_billing data for {autobill[0]}')
            config.log.debug(f'\n{copy}')

            cur = conn.cursor()
            with open(f'{ab_id}.csv', 'a') as f_output:
                f_output.write("transaction_billing\r\n")
                cur.copy_expert(copy, f_output)
        except Exception:
            config.log.exception('SELECT failed')
            raise sys.exc_info()[0]

        # Get the latest transaction_billing_item rows for this autobill.id where
        # the transaction_billing status is "Success" (6) (aka "Paid") or
        # "Settlement" (10), aka "Due"
        sql = f'select \
tbi.id, \
transaction_billing_id, \
tb.merchant_txb_identifier , \
tbit."type" , \
tbi.index_number , \
quantity , \
tbi.amount, \
tbi.subtotal, \
tbi.tax_total, \
tbi.total, \
 sku.sku, \
 sku_description.description \
from transaction_billing_item tbi \
join transaction_billing tb on tb.id = tbi.transaction_billing_id \
join sku on sku.id = sku_id \
join sku_description on sku_description.id = tbi.sku_description_id \
left join transaction_bill_item_type tbit on \
	tbit.id = tbi.transaction_bill_item_type_id \
where transaction_billing_id = ( \
	select  max(id) \
	from  transaction_billing tb \
	where tb.autobill_id = {autobill[0]} \
		and cur_transaction_bill_status_id in (6, 10) ) \
order by transaction_billing_id, tbi.index_number asc'

        copy = f'COPY ({sql}) TO STDOUT WITH CSV HEADER FORCE QUOTE *'

        try:
            config.log.info(f'Getting transaction_billing_item data for {autobill[0]}')
            config.log.debug(f'\n{copy}')

            cur = conn.cursor()
            with open(f'{ab_id}.csv', 'a') as f_output:
                f_output.write("transaction_billing\r\n")
                cur.copy_expert(copy, f_output)
        except Exception:
            config.log.exception('SELECT failed')
            raise sys.exc_info()[0]

        # Get the transactions for an AutoBill by database id
        sql = f'select \
tx.id, \
tx.autobill_id, \
tb.merchant_txb_identifier, \
merchant_tx_identifier, \
tx.amount, \
refund_index , \
recurring , \
autobill_cycle , \
billing_plan_cycle, \
tdt.description "status", \
tt.type, \
current_merchant_ts, \
type_id \
from transaction tx \
join tx_disposition_type tdt on tdt.id = tx.current_disposition_id \
join transaction_type tt on tt.id = tx.type_id \
left join transaction_bill_transaction tbt on tbt.transaction_id = tx.id \
left join transaction_billing tb on tbt.transaction_billing_id = tb.id \
where tx.autobill_id in (\'{autobill[0]}\') \
order by autobill_cycle asc, current_merchant_ts asc'
        # print(sql)

        copy = f'COPY ({sql}) TO STDOUT WITH CSV HEADER FORCE QUOTE *'
        try:
            cur = conn.cursor()
            config.log.info(f'Getting transaction data for {autobill[0]}')
            config.log.debug(f'\n{copy}')

            with open(f'{ab_id}.csv', 'a') as f_output:
                f_output.write("transaction\r\n")
                cur.copy_expert(copy, f_output)
        except Exception:
            config.log.exception('SELECT failed')
            raise sys.exc_info()[0]
    return

if __name__ == '__main__':
    import config
    # create new Subscription and get data
    if (config.args.nocreate and not config.args.getdata):
        config.log.warning('Why are you here if --nocreate and not --getdata?')
    elif (config.args.nocreate and config.args.getdata):
        config.log.info(f'Only getting data for existing Subscription >{config.args.autobillid}<')
        if (config.args.autobillid):
            pass
            db_getdbdata(config.args.autobillid)
        else:
            config.log.info(f'Need a Subscription.id to retrieve data from the database')
    elif (not config.args.nocreate and config.args.getdata):
        config.log.info('Create new Subscription and get transaction_billing data')
        response = create()
        db_getdbdata(response['id'])
    else:
        config.log.info('Create new Subscription only')
        response = create()
