'''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


Created on Nov 20, 2009
Author: Paul Trippett (paul@getyouridx.com)
'''

import httplib
import base64
import time
import datetime

import iso8601
from xml.dom import minidom


class ChargifyError(Exception):
    """
    A Chargify Releated error
    @license    GNU General Public License
    """
    pass

class ChargifyUnAuthorized(ChargifyError):
    """
    Returned when API authentication has failed.
    @license    GNU General Public License
    """
    pass

class ChargifyForbidden(ChargifyError):
    """
    Returned by valid endpoints in our application that have not been enabled for API use.
    @license    GNU General Public License
    """
    pass

class ChargifyNotFound(ChargifyError):
    """
    The requested resource was not found.
    @license    GNU General Public License
    """
    pass

class ChargifyUnProcessableEntity(ChargifyError):
    """
    Sent in response to a POST (create) or PUT (update) request that is invalid.
    @license    GNU General Public License
    """
    pass

class ChargifyServerError(ChargifyError):
    """
    Signals some other error
    @license    GNU General Public License
    """
    pass


class ChargifyBase(object):
    """
    The ChargifyBase class provides a common base for all classes in this module
    @license    GNU General Public License
    """
    __ignore__ = ['api_key', 'sub_domain', 'base_host', 'request_host', 'id', '__xmlnodename__']
    
    api_key = ''
    sub_domain = ''
    base_host = '.chargify.com'
    request_host = ''
    
    def __init__(self, apikey, subdomain):
        """
        Initialize the Class with the API Key and SubDomain for Requests to the Chargify API
        """
        self.api_key = apikey
        self.sub_domain = subdomain
        self.request_host = self.sub_domain + self.base_host
    
    def __get_xml_value(self, nodelist):
        """
        Get the Text Value from an XML Node
        """
        rc = ""
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
        return rc
    
    def __get_object_from_node(self, node, obj_type = ''):
        """
        Copy values from a node into a new Object
        """
        if obj_type == '':
            constructor = globals()[self.__name__]
        else:
            constructor = globals()[obj_type]
        obj = constructor(self.api_key, self.sub_domain)
        
        for childnodes in node.childNodes:
            if childnodes.nodeType == 1 and not childnodes.nodeName == '':
                if childnodes.nodeName in self.__attribute_types__:
                    obj.__setattr__(childnodes.nodeName, self._applyS(childnodes.toxml(), self.__attribute_types__[childnodes.nodeName], childnodes.nodeName))
                else:
                    node_value = self.__get_xml_value(childnodes.childNodes)
                    if "type" in  childnodes.attributes.keys():
                        node_type = childnodes.attributes["type"]
                        if node_value:
                            if node_type.nodeValue == 'datetime':
                                node_value = datetime.datetime.fromtimestamp(iso8601.parse(node_value))
                    obj.__setattr__(childnodes.nodeName, node_value)
        
        return obj
    
    def _applyS(self, xml, obj_type, node_name):
        """
        Apply the values of the passed xml data to the a class
        """
        dom = minidom.parseString(xml)
        nodes = dom.getElementsByTagName(node_name)
        if nodes.length == 1:
            return self.__get_object_from_node(nodes[0], obj_type)
        
    def _applyA(self, xml, obj_type, node_name):
        """
        Apply the values of the passed data to a new class of the current type
        """
        dom = minidom.parseString(xml)
        nodes = dom.getElementsByTagName(node_name)
        objs = []
        for node in nodes:
            objs.append(self.__get_object_from_node(node, obj_type))
        return objs
    
    def _toxml(self, dom):
        """
        Return a XML Representation of the object
        """
        element = minidom.Element(self.__xmlnodename__)
        for property, value in self.__dict__.iteritems():
            if not property in self.__ignore__:
                if property in self.__attribute_types__:
                    element.appendChild(value._toxml(dom))
                else:
                    node = minidom.Element(property)
                    node_txt = dom.createTextNode(str(value))
                    node.appendChild(node_txt)
                    element.appendChild(node)
        return element
    
    def _get(self, url):
        """
        Handle HTTP GET's to the API
        """
        headers = {
            "Authorization": "Basic %s" % self._get_auth_string(),
            "User-Agent": "pyChargify",
            "Content-Type": "text/xml"
        }
        
        r = httplib.HTTPSConnection(self.request_host)
        r.request('GET', url, None, headers)
        response = r.getresponse()
        
        # Unauthorized Error
        if response.status == 401:
            raise ChargifyUnAuthorized()
        
        # Forbidden Error
        elif response.status == 403:
            raise ChargifyForbidden()
        
        # Not Found Error
        elif response.status == 404:
            raise ChargifyNotFound()
        
        # Unprocessable Entity Error
        elif response.status == 422:
            raise ChargifyUnProcessableEntity()
        
        # Generic Server Errors
        elif response.status in [405, 500]:
            raise ChargifyServerError()
        
        return response.read()
        
    def _post(self, url, data):
        """
        Handle HTTP POST's to the API
        """
        return self._request('POST', url, data)
    
    def _put(self, url, data):
        """
        Handle HTTP PUT's to the API
        """
        return self._request('PUT', url, data)
    
    def _delete(self, url, data):
        """
        Handle HTTP DELETE's to the API
        """
        return self._request('DELETE', url, data)
    
    def _request(self, method, url, data = '' ):
        """
        Handled the request and sends it to the server
        """
        http = httplib.HTTPSConnection(self.request_host)
        
        http.putrequest(method, url)
        http.putheader("Authorization", "Basic %s" % self._get_auth_string())
        http.putheader("User-Agent", "pychargify")
        http.putheader("Host", self.request_host)
        http.putheader("Accept", "application/xml")
        http.putheader("Content-Length", str(len(data)))
        http.putheader("Content-Type", 'text/xml; charset="UTF-8"')
        http.endheaders()

        http.send(data)
        response = http.getresponse()
        
        # Unauthorized Error
        if response.status == 401:
            raise ChargifyUnAuthorized()
        
        # Forbidden Error
        elif response.status == 403:
            raise ChargifyForbidden()
        
        # Not Found Error
        elif response.status == 404:
            raise ChargifyNotFound()
        
        # Unprocessable Entity Error
        elif response.status == 422:
            raise ChargifyUnProcessableEntity()
        
        # Generic Server Errors
        elif response.status in [405, 500]:
            raise ChargifyServerError()
        
        return response.read()
    
    def _save(self, url, node_name):
        """
        Save the object using the passed URL as the API end point
        """
        dom = minidom.Document()
        dom.appendChild(self._toxml(dom))
        
        print dom.toprettyxml(encoding="utf-8")
        
        request_made = {
            'day': datetime.datetime.today().day,
            'month': datetime.datetime.today().month,
            'year': datetime.datetime.today().year
        }
        
        if self.id:
            obj = self._applyS(self._put('/' + url + '/' + self.id + '.xml', dom.toxml(encoding="utf-8")), self.__name__, node_name)
            if obj:
                if type(obj.updated_at) == datetime.datetime:
                    if (obj.updated_at.day == request_made['day']) and (obj.updated_at.month == request_made['month']) and (obj.updated_at.year == request_made['year']):
                        self.saved = True
                        return (True, obj)
            return (False, obj)
        else:
            obj = self._applyS(self._post('/' + url + '.xml', dom.toxml(encoding="utf-8")), self.__name__, node_name)
            if obj:
                if type(obj.updated_at) == datetime.datetime:
                    if (obj.updated_at.day == request_made['day']) and (obj.updated_at.month == request_made['month']) and (obj.updated_at.year == request_made['year']):
                        return (True, obj)
            return (False, obj)
    
    def _get_auth_string(self):
        return base64.encodestring('%s:%s' % (self.api_key, 'x'))[:-1]


class ChargifyCustomer(ChargifyBase):
    """
    Represents Chargify Customers
    @license    GNU General Public License
    """
    __name__ = 'ChargifyCustomer'
    __attribute_types__ = {}
    __xmlnodename__ = 'customer'
    
    id = None
    first_name = ''
    last_name = ''
    email = ''
    organization = ''
    reference = ''
    created_at = None
    modified_at = None
    
    def __init__(self, apikey, subdomain, nodename = ''):
        super( ChargifyCustomer, self ).__init__(apikey, subdomain)
        if nodename:
            self.__xmlnodename__ = nodename
        
    def getAll(self):
        return self._applyA(self._get('/customers.xml', self.__name__, 'customer'))
    
    def getById(id):
        return self._applyS(self._get('/customers/' + str(id) + '.xml', self.__name__, 'customer'))
    
    def getByHandle(handle):
        return self._applyS(self._get('/customers/' + str(handle) + '.xml', self.__name__, 'customer'))
    
    def getSubscriptions(self):
        obj = ChargifySubscription()
        return obj.getByCustomerId(self.id)
    
    def save(self):
        return self._save('customers', 'customer')
    

class ChargifyProduct(ChargifyBase):
    """
    Represents Chargify Products
    @license    GNU General Public License
    """
    __name__ = 'ChargifyProduct'
    __attribute_types__ = {}
    __xmlnodename__ = 'product'
    
    id = None
    price_in_cents = 0
    name = ''
    handle = ''
    product_family = {}
    accounting_code = ''
    interval_unit = ''
    interval = 0
    
    def __init__(self, apikey, subdomain, nodename = ''):
        super( ChargifyProduct, self ).__init__(apikey, subdomain)
        if nodename:
            self.__xmlnodename__ = nodename

    def getAll(self):
        return self._applyA(self._get('/products.xml'), self.__name__, 'product')
    
    def getById(self, id):
        return self._applyS(self._get('/products/' + str(id) + '.xml'), self.__name__, 'product')
    
    def getByHandle(self, handle):
        return self._applyS(self._get('/products/handle/' + str(handle) + '.xml'), self.__name__, 'product')
    
    def getPaymentPageUrl(self):
        return 'https://' + self.request_host + '/h/' + self.id + '/subscriptions/new'
    
    def save(self):
        return self._save('products', 'product')
    
    def getPriceInDollars(self):
        return round(float(self.price_in_cents) / 100, 2)


class ChargifySubscription(ChargifyBase):
    """
    Represents Chargify Subscriptions
    @license    GNU General Public License
    """
    __name__ = 'ChargifySubscription'
    __attribute_types__ = {
        'customer': 'ChargifyCustomer',
        'product': 'ChargifyProduct',
        'credit_card': 'ChargifyCreditCard'
    }
    __xmlnodename__ = 'subscription'
    
    id = None
    state = ''
    balance_in_cents = 0
    current_period_started_at = None
    current_period_ends_at = None
    trial_started_at = None
    trial_ended_attrial_ended_at = None
    activated_at = None
    expires_at = None
    created_at = None
    updated_at = None
    customer = None
    product = None
    product_handle = ''
    credit_card = None
    
    def __init__(self, apikey, subdomain, nodename = ''):
        super( ChargifySubscription, self ).__init__(apikey, subdomain)
        if nodename:
            self.__xmlnodename__ = nodename
    
    def getByCustomerId(self, customer_id):
        return self._applyA(self._get('/customers/' + customer_id + '/subscriptions.xml'), self.__name__, 'subscription')
    
    def getBySubscriptionId(self, subscription_id):
        return self._applyA(self._get('/subscriptions/' + subscription_id + '.xml'), self.__name__, 'subscription')

    def save(self):
        return self._save('subscriptions', 'subscription')


class ChargifyCreditCard(ChargifyBase):
    """
    Represents Chargify Credit Cards
    """
    __name__ = 'ChargifyCreditCard'
    __attribute_types__ = {}
    __xmlnodename__ = 'credit_card_attributes'
    
    first_name = ''
    last_name = ''
    full_number = ''
    masked_card_number = ''
    expiration_month = ''
    expiration_year = ''
    cvv = ''
    type = ''
    billing_address = ''
    billing_city = ''
    billing_state = ''
    billing_zip = ''
    billing_country = ''
    
    def __init__(self, apikey, subdomain, nodename = ''):
        super( ChargifyCreditCard, self ).__init__(apikey, subdomain)
        if nodename:
            self.__xmlnodename__ = nodename


class ChargifyPostBack(ChargifyBase):
    """
    Represents Chargify API Post Backs
    @license    GNU General Public License
    """
    def __init__(self, apikey):
        ChargifyBase.__init__(apikey, subdomain)


class Chargify:
    """
    The Chargify class provides the main entry point to the Charify API
    @license    GNU General Public License
    """
    api_key = ''
    sub_domain = ''
    
    def __init__(self, apikey, subdomain):
        self.api_key = apikey
        self.sub_domain = subdomain
    
    def Customer(self, nodename = ''):
        return ChargifyCustomer(self.api_key, self.sub_domain, nodename)
    
    def Product(self, nodename = ''):
        return ChargifyProduct(self.api_key, self.sub_domain, nodename)

    def Subscription(self, nodename = ''):
        return ChargifySubscription(self.api_key, self.sub_domain, nodename)

    def CreditCard(self, nodename = ''):
        return ChargifyCreditCard(self.api_key, self.sub_domain, nodename)
        