#!/usr/bin/env python

import api

def print_spacer():
    print ""
    print "################################################################################"
    print ""

def print_product(item):
    print "#########################################"
    print "# '" + item.name + "' Product"
    print "#########################################"
    print "Id:              " + item.id
    print "Price in Cents:  " + item.price_in_cents
    print "Name:            " + item.name
    print "Handle:          " + item.handle
    print "Accounting Code: " + item.accounting_code
    print "Interval Unit:   " + item.interval_unit
    print "Interval:        " + item.interval
    print " "
    

# Initialize the API with the API Key and the sub domain
chargify = api.Chargify('YOUR-API-KEY', 'YOUR-SUB-DOMAIN')

# Get All Products
#print "Get All Products: "
#print ""
#for item in chargify.Product().getAll():
#    print_product(item)


#print_spacer()


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
print "Save a Subscription: "
print ""

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

subscription.save()

