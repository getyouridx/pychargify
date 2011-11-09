#!/usr/bin/env python
''' Test the Pychargify Library.
    Edit my chargify = line with API key, then run me.
'''

import api


def print_spacer(repeat=70):
    ''' Print a spacer line, 70 chars across '''
    print "\n" + "#" * repeat + "\n"


def print_product(item):
    ''' Print out a little formatted product info item. '''
    product_info = ''' #########################################
 ''' + item.name + ''' Product
#########################################
Id:              ''' + item.id + '''
Price in Cents:  ''' + item.price_in_cents + '''
Name:            ''' + item.name + '''
Handle:          ''' + item.handle + '''
Accounting Code: ''' + item.accounting_code + '''
Interval Unit:   ''' + item.interval_unit + '''
Interval:        ''' + item.interval + '''
'''
    print product_info


def run_test():
    ''' Init the API, and run some sample queries. '''
# Initialize the API with the API Key and the sub domain
    chargify = api.Chargify('YOUR-API-KEY', 'YOUR-SUB-DOMAIN')

# Get All Products
    print "Get All Products: \n"
    for item in chargify.Product().getAll():
        print_product(item)

    print_spacer()
    # Get a Single Product by its ID
    #print "Get a Product By its ID: "
    #print ""
    #print_product(chargify.Product().getById(161))
    #print_spacer()

    # Get a Single Product by its Handle
    #print "Get a Product By its Handle: "
    #print ""
    #print_product(chargify.Product().getByHandle('plus'))
    #print_spacer()

    # Get a Single Product by its Handle
    print "Save a Subscription: \n"

    customer = chargify.Customer('customer_attributes')
    customer.first_name = 'Paul'
    customer.last_name = 'Trippett'
    customer.email = 'paul@getyouridx.com'

    creditcard = chargify.CreditCard('credit_card_attributes')
    creditcard.full_number = 1
    creditcard.expiration_month = 10
    creditcard.expiration_year = 2020

    subscription = chargify.Subscription()
    subscription.product_handle = 'fhaar-mini'
    subscription.customer = customer
    subscription.credit_card = creditcard

    if subscription.save():
        print "Subscription Created Successfully"
    else:
        print "Subscription Creation Failed"

if __name__ == "__main__":
    run_test()
