Chargify API wrapper for Python
===============================

pychargify
----------

This is a Python wrapper for the [Chargify](http://chargify.com) API. It allows you to interface
with the Chargify API using a simple object orientated syntax.

    chargify = Chargify('YOUR-API-KEY', 'YOUR-SUB-DOMAIN')
    
    customer = chargify.Customer('customer_attributes')
    customer.first_name = 'John'
    customer.last_name = 'Doe'
    customer.email = 'john@doe.com'
    customer.save()

See tests.py for more usage examples.


### Installation

Place this library in your project and import the module

    from pychargify.api import *


### Requirements

This library has no special requirements

### Usage

Simply import this library before you use it:

    from pychargify.api import *
    

Now you'll have access to classes the interact with the Chargify API, such as:

`Chargify`  
`ChargifyProduct`  
`ChargifyCustomer`  
`ChargifiySubscription`
`ChargifiyCreditCard`

`Chargify` is a helper class that makes initialization easier of the `ChargifyProduct`, `ChargifyCustomer`,
`ChargifiySubscription` and `ChargifiyCreditCard` classes


### Contributors

* Paul Trippett (GetYourIDX)