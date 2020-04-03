#!/usr/bin/env python
# Use SOAP AutoBill::makePayment() API to record payment against 1 or more Subscribe invoices
#
# Invoice IDs are supplied in a file 'makePayment.in' in the current directory.
# Invoices are retrieved from Subscribe one at a time and if the invoice
# balance is > 0, the AutoBill.makePayment SOAP API is called with the
# outstanding amount of the invoice
#

import json
import logging
import os
from datetime import date, datetime, timedelta
import decimal
import time
import requests

from mylib.utils import *

def toISOdatetime(strdate):
    return datetime.strptime(strdate, '%Y-%m-%dT%H:%M:%S%z')

def main():
    import config

    api_base = 'https://api.prodtest.vindicia.com'

    # /invoices?subscription=vin-soap-ab-20190928:131658&status=Due'
    loop = 0

    with open('makePayment.in', 'r') as f:
        for line in f:
            loop = loop+1
            line = line.rstrip('\n')
            if (not len(line)):
                continue
            parts = line.split(',')
            # log.info('>%s<  >%s<  >%s<', parts[0], parts[1], parts[2])

            url = api_base + '/invoices/' + parts[0]
            config.log.info(url)
            r = requests.get(url, auth=(config.API_CREDS[0], config.API_CREDS[1]))
            if (r.ok):
                data = r.json()
                isodate = toISOdatetime(data['invoice_date'])             
                if (data['invoice_balance'] > 0):
                    config.log.info('>%s< Due from >%s< for invoice >%s<\tPay date %s',
                        data['invoice_balance'], isodate, data['id'],
                        isodate+timedelta(days=3))
                    # dict for vinProxy SOAP request
                    api_body = {
                        "srd": "",
                        "autobill": {
                            "merchantAutoBillId": data['subscription']['id']
                        },
                        "paymentMethod": {
                            "merchantPaymentMethodId": "vin-soap-,ap-pm-" + config.suffix + '.' + str(loop),
                            "accountHolderName": "Payment1",
                            "type": "MerchantAcceptedPayment",
                            "merchantAcceptedPayment": {
                                "account": "1111111111",
                                "note": "Payment made on " + config.suffix,
                                "paymentId":  config.suffix + '.' + str(loop),
                                "paymentType": "Bogus Payment Type",
                            }
                        },
                        "amount": data['invoice_balance'],
                        "currency": data['invoice_currency'],
                        "invoiceId": data['id'],
                        "overageDisposition": "applyToOldestInvoice",
                        "note": "Invoice payment"
                    }
                    try:
                        response = vinProxy('AutoBill.makePayment', api_body)

                    except Exception:
                        config.log.exception('AutoBill.makePayment error')
                        return api_return('502', 'AutoBill.update error')
                    config.log.debug('ddd %s', json.dumps(response, default=json_serial, indent=4))
                    # print(api_body)
                else:
                    config.log.info('No payment Due for invoice >%s<', data['id'])
            else:
                config.log.warning('%s - %s for invoice >%s<', r.status_code, r.reason, parts[0])


if __name__ == '__main__':
    main()