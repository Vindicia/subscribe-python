#!/usr/bin/env python
# Using SOAP AutoBill.update via vinProxy, create a new AutoBill

# Arguments:
#     autobill {dict} -- Python dictionary corresponding to the AutoBill to
#         be created. See CashBox AutoBill Data Members documentation for key names

# Returns:
#     dict -- Dictionary corresponsing to AutoBillUpdateReturn
#

import json
import logging
import os
from datetime import date, datetime
import decimal
import time
import requests

import config
from utils import *

def newAutoBill(requestBody: dict):
    if (requestBody['policy']):
        # Use REST
        url = f'https://{config.rest_host}/subscriptions?dryrun={config.args.dryrun}'
        # config.log.info(json.dumps(requestBody, indent=4, default=json_serial))
        # return "Poser"
        try:
            config.log.debug(json.dumps(requestBody, indent=4, default=json_serial))
            r = requests.post(url, auth=(config.API_CREDS[0], config.API_CREDS[1]), json = requestBody)
            config.log.info('%s\t%s\t%s', r.headers['Request-Id'], r.status_code, r.reason)
            if (r.ok):
                response = r.json()
            else:
                sys.exit(r.status_code)
        except Exception:
            config.log.exception('Subscriptions create error\n%s', json.dumps(r.headers, indent=4))
            # response = r
    else:
        # Use SOAP proxy to perform AutoBill.fetchByVid()
        try:
            # return autobill
            response = vinProxy('AutoBill.update', requestBody)
        except Exception:
            config.log.exception('AutoBill.update error')
            return api_return('502', 'AutoBill.update error')
        # config.log.debug('%s', json.dumps(response, default=json_serial, indent=4))
    return response

if __name__ == '__main__':
    address = {
        'name': config.args.name,
        'addr1': config.args.addr1,
        'city': config.args.city,
        'district': config.args.district,
        'postalCode': config.args.postalcode,
        'country': config.args.country,
        'phone': config.args.phone
    }
    account = {
        'merchantAccountId': config.args.autobillid,
        'defaultCurrency': config.args.defaultcurrency,
        'emailAddress': config.args.email,
        'emailTypePreference': config.args.emailtypepreference,
        'preferredLanguage': config.args.preferredlanguage,
        'name': config.args.name,
        'shippingAddress': address
    }
    billingPlan =  {
        'merchantBillingPlanId': config.args.billingplanid
    }

    paymentMethod = {
        'merchantPaymentMethodId': config.args.paymentid,
        'accountHolderName': config.args.name,
        'billingAddress': {
            'name': config.args.name,
            'addr1': config.args.addr1,
            'city': config.args.city,
            'district': config.args.district,
            'postalCode': config.args.postalcode,
            'country': config.args.country,
            'phone': config.args.phone
        }
    }
    if config.args.map:
        merchantAcceptedPayment = {
            'paymentType': ''
        }
        paymentMethod['type'] = 'MerchantAcceptedPayment'
        paymentMethod['merchantAcceptedPayment'] = merchantAcceptedPayment
    elif config.args.paypal:
        paypal = {
            'returnUrl': config.args.paypalreturn,
            'cancelUrl': config.args.paypalcancel
        }
        paymentMethod['type'] = 'PayPal'
        paymentMethod['paypal'] = paypal
    else:
        creditCard = {
            'account': config.args.creditcard,
            'expirationDate': config.args.expirationdate
        }
        # Set the CVN name/value for this PaymentMethod
        cvn = {
            'name': 'CVN',
            'value': config.args.cvn
        }
        # Put credit card  data into PaymentMethod object
        paymentMethod['type'] = 'CreditCard'
        paymentMethod['creditCard'] = creditCard
        paymentMethod['nameValues'] = [cvn]

    items = [
        {
            'merchantAutoBillItemId': config.args.autobillid+'.001',
            'index': '0',
            'product': {
                'merchantProductId': config.args.productid
            }
        }
    ]

    autobill =  {
        'merchantAutoBillId': config.args.autobillid,
        'account': account,
        'billingPlan': billingPlan,
        'paymentMethod': paymentMethod,
        'currency': config.args.defaultcurrency,
        'customerAutoBillName': config.args.autobillid,
        'items': items,
        'sourceIp': '192.168.1.1',
        'nameValues': [
            {
                'name': 'merchant_data_name',
                'value': 'merchant_data_value'
            }
        ],
        'startTimestamp': config.args.starttimestamp
    }

    requestBody = {
        'srd': '',
        'autobill': autobill,
        'immediateAuthFailurePolicy': config.args.immediateauthfailurepolicy,
        'validateForFuturePayment': int(config.args.validateforfuturepayment),
        'minChargebackProbability': config.args.minchargebackprobability,
        'ignoreAvsPolicy': int(config.args.ignoreavspolicy),
        'ignoreCvnPolicy': int(config.args.ignorecvnpolicy),
        'dryrun': int(config.args.dryrun),
        'initialAuth': config.args.initialauth
    }

    response = newAutoBill(requestBody)
    config.log.debug(json.dumps(response, indent=4, default=json_serial))
