#!/usr/bin/env python

import api
from print_r import print_r

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
chargify = api.Chargify('YOUR-CHARGIFY-API-KEY', 'YOUR-CHARGIFY-SUB-DOMAIN')

# Get All Products
print "Get All Products: "
print ""
for item in chargify.Products.getAll():
    print_product(item)


print_spacer()


# Get a Single Product by its ID
print "Get a Product By its ID: "
print ""
print_product(chargify.Products.getById(161))


print_spacer()


# Get a Single Product by its Handle
print "Get a Product By its Handle: "
print ""
print_product(chargify.Products.getByHandle('plus'))

