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
from print_r import print_r
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
                    obj.__setattr__(childnodes.nodeName, self._applyS(childnodes, self.__attribute_types__[childnodes.nodeName]))
                else:
                    obj.__setattr__(childnodes.nodeName, self.__get_xml_value(childnodes.childNodes))
        
        return obj
    
    def _applyS(self, xml, node_name):
        """
        Apply the values of the passed xml data to the a class
        """
        dom = minidom.parseString(xml)
        nodes = dom.getElementsByTagName(node_name)
        if nodes.length == 1:
            return self.__get_object_from_node(nodes[0])
        
    def _applyA(self, xml, node_name):
        """
        Apply the values of the passed data to a new class of the current type
        """
        dom = minidom.parseString(xml)
        nodes = dom.getElementsByTagName(node_name)
        objs = []
        for node in nodes:
            objs.append(self.__get_object_from_node(node))
        return objs
    
    def _get(self, url):
        """
        Handle HTTP GET's to the API
        """
        return self._request('GET', url)
    
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
    
    def _request(self, method, url, data = None  ):
        r = httplib.HTTPSConnection(self.request_host)
        headers = {"Authorization": "Basic %s" % self.get_auth_string(), "User-Agent": "pyChargify"}
        r.request(method, url, data, headers)
        response = r.getresponse()
        
        if response.status == '200':
            pass
        elif response.status == '201':
            pass
        elif response.status == '401':
            raise ChargifyUnAuthorized()
        elif response.status == '403':
            raise ChargifyForbidden()
        elif response.status == '404':
            raise ChargifyNotFound()
        elif response.status == '422':
            raise ChargifyUnProcessableEntity()
        elif response.status == '500':
            raise ChargifyServerError()
        
        return response.read()
    
    def get_auth_string(self):
        return base64.encodestring('%s:%s' % (self.api_key, 'x'))[:-1]


class ChargifyCustomer(ChargifyBase):
    """
    Represents Chargify Customers
    @license    GNU General Public License
    """
    __name__ = 'ChargifyCustomer'
    __attribute_types__ = {}
    
    id = None
    first_name = ''
    last_name = ''
    email = ''
    organization = ''
    reference = ''
    created_at = None
    modified_at = None
    
    def __init__(self, apikey, subdomain):
        super( ChargifyCustomer, self ).__init__(apikey, subdomain)
        
    def getAll(self):
        return self._applyA(self._get('/customers.xml', 'customer'))
    
    def getById(id):
        return self._applyS(self._get('/customers/' + str(id) + '.xml', 'customer'))
    
    def getByHandle(handle):
        return self._applyS(self._get('/customers/' + str(handle) + '.xml', 'customer'))
    
    def getSubscriptions(self):
        obj = ChargifySubscription()
        return obj.getByCustomerId(self.id)
    

class ChargifyProduct(ChargifyBase):
    """
    Represents Chargify Products
    @license    GNU General Public License
    """
    __name__ = 'ChargifyProduct'
    __attribute_types__ = {}
    
    id = None
    prince_in_cents = 0
    name = ''
    handle = ''
    product_family = {}
    accounting_code = ''
    interval_unit = ''
    interval = 0
    
    def __init__(self, apikey, subdomain):
        super( ChargifyProduct, self ).__init__(apikey, subdomain)

    def getAll(self):
        return self._applyA(self._get('/products.xml'), 'product')
    
    def getById(self, id):
        return self._applyS(self._get('/products/' + str(id) + '.xml'), 'product')
    
    def getByHandle(self, handle):
        return self._applyS(self._get('/products/handle/' + str(handle) + '.xml'), 'product')


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
    credit_card = None
    
    def __init__(self, apikey, subdomain):
        ChargifyBase.__init__(apikey, subdomain)
    
    def getByCustomerId(self, customer_id):
        return self._applyA(self._get('/customers/' + customer_id + '/subscriptions.xml'), 'subscription')
    
    def getBySubscriptionId(self, subscription_id):
        return self._applyA(self._get('/subscriptions/' + subscription_id + '.xml'), 'subscription')


class ChargifyCreditCard(ChargifyBase):
    """
    Represents Chargify Credit Cards
    """
    __name__ = 'ChargifyCreditCard'
    __attribute_types__ = {}
    
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
    apikey = ''
    Customers = None
    Products = None
    def __init__(self, apikey, subdomain):
        self.apikey = apikey
        self.Customers = ChargifyCustomer(self.apikey, subdomain)
        self.Products = ChargifyProduct(self.apikey, subdomain)
    
