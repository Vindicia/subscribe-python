# Python Suscribe Create
============================

I had need to create Subscriptions with both CreditCard and MerchantAcceptedPayment payment methods and collect relevant 
transaction, transaction_billing and transaction_billing_item data from the database.

## Usage
----------------------------
```create-subscription.py -h
-------------------------------------------------------------------------------
Python wrapper for Subscribe

optional arguments:
  -h, --help            show this help message and exit
  --debug debug         Integer debug level for this script
  --nocreate            If set, new Subscription creation will be skipped.
  --getdata             If set, no database queries are perfomed to get
                        transaction details for a Subscription.
  --accountid <accountid>
                        Merchant identifier for Account object
  --name <customer full name>
                        The customer’s name, usually corresponding to name on
                        credit card
  --addr1 <address line 1>
                        First line of address.
  --addr2 <address line 2>
                        Second line of address
  --city <city>         Address city
  --district <state/province>
                        Address state/province
  --county <county>     Address county
  --country <country>   Address country
  --postalcode <postalCode>
                        Customer zip/postal code
  --phone <phone>       Customer phone number
  --defaultcurrency <code>
                        ISO 4217 currency code to use for this operation
  --preferredlanguage <code>
                        W3C IANA Language Subtag Registry code for customer
                        preferred language
  --email <email>       Customer email address
  --emailtypepreference {html,plaintext}
                        Customer preferred format for email messages
  --externalid <externalId>
                        Merchant additional unique identifier for this
                        Account. Uniqueness or null for this value is enforced
                        by Subscribe per Merchant
  --paymentid <paymentid>
                        Merchant identifier for PaymentMethod object
  --creditcard creditcard
                        Credit card account number
  --expirationdate <YYYYMM>
                        4 Digit year and 2 digit month of credit card
                        expiration date (YYYYMM). Defaults to 1 year from
                        today
  --cvn cvn             Card Verification Number
  --map                 Flag to trigger use of MerchantAcceptedPayment payment
                        method for purchase
  --paypal              Flag to trigger PayPal PaymentMethod for CashBox
                        operation
  --paypalnoshippingaddress
                        Flag to trigger masking of the PayPal shipping address
                        for customers buying digital goods.
  --paypalcancel <url>  URL to which to redirect if PayPal indicates failure
                        after completeing payment process on PayPal site
  --paypalreturn <url>  URL to which to redirect after successfully
                        completeing payment transactions on PayPal site
  --autobillid <autobillid>
                        Merchant identifier for AutoBill object
  --starttimestamp <YYYY-MM-DDTHH:MM:SS>
                        A time stamp that specifies the start date and time
                        for this AutoBill object. If unspecified, the value
                        defaults to today and the current time.
  --invoiceterms n      The number of days after the invoice date that a bill
                        is considered delinquent, if the AutoBill payment
                        method is MerchantAcceptedPayment. This value will be
                        ignored for all other payment methods.
  --specifiedbillingday n
                        Integer (1-31) specifying the day of the month on
                        which to bill (values 29-31 automatically work as the
                        last day of the month for calendar months that do not
                        have 29, 30, or 31 days). Providing no value or null
                        in this parameter instructs CashBox to bill on the
                        service period start date (the default)
  --billingrule <billingrule>
                        An enumerated string value (Advance or Arrears),
                        informing CashBox in which direction from the
                        scheduled billing date to select the specified billing
                        date. If no specified_billing_day is provided, this
                        parameter is ignored.
  --billingplanid <merchantBillingplanId>
                        Merchant identifier for BillingPlan object
  --productid [<productid> [<productid> ...]]
                        One or more CashBox Product object identifiers for
                        items of the subscription
  --cycles n            The number of billing cycles this item will be active
  --transactionid <merchantTransactionId>
                        Merchant unique identifier for a CashBox Transaction
                        object
  --taxclassification [<taxClassification> [<taxClassification> ...]]
                        Tax classification override, appropriate for tax
                        engine, for this item(s). Applied positionally to
                        individual items
  --itemsku [sku [sku ...]]
                        Product identifier(s) for item(s). Only used in
                        context of one-time transactions
  --itemname [itemname [itemname ...]]
                        Product name(s) for item(s). Only used in context of
                        one-time transactions
  --itemprice [<itemprice> [<itemprice> ...]]
                        Price(s) to be applied positionally to individual
                        items
  --itemqty [itemqty [itemqty ...]]
                        Product quantity(ies) for item(s)
  --itemstartdate [<YYYY-MM-DD> [<YYYY-MM-DD> ...]]
                        Start date to be used for AutoBill. Defaults to script
                        runtime
  --itemcampaign [<campaigCode> [<campaigCode> ...]]
                        Campaign code(s) to be applied positionally to
                        individual items
  --itemcycles [n [n ...]]
                        Fixed count of billing cycles to be used for item(s).
                        Applied positionally to individual items
  --srd <srd>           Sparse Response Description, a SOAP string (which must
                        be a JSON object), specifying the CashBox data
                        elements to be returned by the operation
  --cancelreason cancelreason
                        Integer reason code for canceling the AutoBill
  --campaigncode <campaignCode>
                        String Coupon or Promotion code, from CashBox
                        Campaign, to apply discount on this AutoBill
  --dryrun              Flag that, if set, will return updated AutoBill,
                        without recording the result in the CashBox database
  --replaceonallautobills
                        Flag that, if set, causes the update of a payment
                        method to propagate to all the AutoBill objects
                        associated with the Account object
  --replaceonallchildautobills
                        Flag that, if set, causes the update of a payment
                        method to propagate to all the AutoBill objects
                        associated with child Accounts of the Account object
  --sendemailnotification
                        Flag that, if set, triggers email notification from
                        CashBox for one-time Transaction operations
  --force               Flag that cancels the subscription even if the minimum
                        commitment period for this AutoBill object has not
                        been satisfied
  --ignoreavspolicy     Flag triggering override of AVS policy to accept the
                        payment method, regardless of the AVS return code from
                        the processor
  --ignorecvnpolicy     Flag triggering override of CVN policy to accept the
                        payment method, regardless of the CVN return code from
                        the processor
  --immediateauthfailurepolicy {doNotSaveAutoBill,putAutoBillInRetryCycle,putAutoBillInRetryCycleIfPaymentMethodIsValid}
                        Enumerated string for behavior if payment method fails
                        validation
  --initialauth {AuthImminentBilling,DelayFullAuthToInitialBillingDate}
                        Enumerated string specifying how to manage
                        authorization and capture when scheduled initial
                        billing is within 25 hours
  --minchargebackprobability n
                        Integer between 0 and 100 identifying fraud risk
                        tolerance level
  --validateforfuturepayment
                        Integer boolean. If true and billing scheduled for
                        future date, triggers minimal authorization ($0/$1)
                        immediately```

## Requirements
============================

### Support files
  ```config.py```
  ----------------------------
    Configuration file for Subscribe python scripts. Salt to taste.
    
    Must include Subscribe API credentials.
    Must include postgres client credentials.
    
    Sets other useful bits like log file location, timezone (if you want to use
    something other than local), command line arguments

  ```utils.py```
  ----------------------------
    Support functions
      ```setup_custom_logger(name)```
        Creates common logging facility
      ```validate(body: dict, sig: str)```
        Validate Subscribe Push Notification message signature using HMAC stored
        in configy.py
      ```json_serial(obj)```
        Serialization helper for data types not directly serializable to JSON
      ```api_return(returnCode, message)```
        api_return helper for standardizing return bodies
      ```verifySignature(string_to_verify, signature, shared_secret)```
        Helper for validate()
      ```ct_compare(a, b)```
        Constant time string comparison
      ```getModificationTx(autobill: dict, event_timestamp: str)```
        Function to get a Transaction of 'vin:type = "modify"' within bounds of a timestamp
      ```getAutoBill(message: dict)```
        SOAP AutoBill.fetchByVid function
      ```vinProxy(method: str, requestBody: dict)```
        SOAP API client
      ```storeMessage(class_id: str, message: dict)```
        Write a 'message' as JSON to an S3 Bucket identified in config.py with a key of 'class_id'
      ```randName()```
        Get a random name from a JSON file
      ```dbconnect()```
        Connect to postgress database using identifiers and credentials stored in config.py
  ```mylib/CharacterNames.json
        JSON for use with randName()

  ```newAutoBill.py```
  ----------------------------
    Module for creating a new Subscription (aka AutoBill). Supports both SOAP (via
    ```vinProxy()```) and REST

3rd Party Modules
----------------------------
  Package           Version   
  ----------------- ----------
  boto3             1.12.22
  psycopg2          2.8.4
  pytz              2019.3
  xmltodict         0.12.0
  zeep              3.4.0

Installation
----------------------------

Clone the repo

Contributing
If you never created a pull request before, welcome :tada: :smile: [Here is a great tutorial](https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github)
on how to send one :)

1. [Fork](http://help.github.com/fork-a-repo/) the project, clone your fork,
   and configure the remotes:

   ```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/<repo-name>
   # Navigate to the newly cloned directory
   cd <repo-name>
   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/apache/<repo-name>
   ```

2. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout master
   git pull upstream master
   ```

3. Create a new topic branch (off the main project development branch) to
   contain your feature, change, or fix:

   ```bash
   git checkout -b <topic-branch-name>
   ```

4. If you added or changed a feature, make sure to document it accordingly in
   the [CouchDB documentation](https://github.com/apache/couchdb-documentation)
   repository.

5. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

6. [Open a Pull Request](https://help.github.com/articles/using-pull-requests/)
    with a clear title and description.



