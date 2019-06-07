"""AXL <updateDevicePool> sample script, using the zeep library

Install Python 2.7 or 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

    $ python -m pip install --upgrade pip

Script Dependencies:
    lxml
    requests
    zeep

Dependency Installation:

    $ pip install zeep

This will install automatically all of zeep dependencies, including lxml, requests

Copyright (c) 2018 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault

# The WSDL is a local file in the working directory, see README

WSDL_FILE = 'AXLAPI.wsdl'

# These are sample values for the DevNet sandbox
# replace them with values for your own CUCM, if needed

CUCM_LOCATION = "10.10.20.1"
USERNAME = 'administrator'
PASSWD = 'ciscopsdt'

# These values assume there is an existing Device Pool with name 'testDevicePool'
# and an existing Route Group named 'testRouteGroup'
# Change as needed

DEVICE_POOL_NAME = 'testDevicePool'
TEST_ROUTE_GROUP_NAME = 'testRouteGroup'
STANDARD_ROUTE_GROUP_NAME = 'testRouteGroup'

# This class lets you view the incoming and outgoing http headers and/or XML

class MyLoggingPlugin(Plugin):

    def egress(self, envelope, http_headers, operation, binding_options):
        print(
'''Request
-------
Headers:
{}

Body:
{}

'''.format( http_headers, 
                etree.tostring(envelope, pretty_print=True, encoding='unicode'))
        )

    def ingress(self, envelope, http_headers, operation):
        print('\n')
        print(
'''Response
-------
Headers:
{}

Body:
{}

'''.format( http_headers, 
                etree.tostring(envelope, pretty_print=True, encoding='unicode'))
        )

# This is where the meat of the application starts
# The first step is to create a SOAP client session

session = Session()

# We avoid certificate verification by default

session.verify = False

# To enabled SSL cert checking (production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth(USERNAME, PASSWD)

transport = Transport(session=session, timeout=10)

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

client = Client(WSDL_FILE, settings=settings, transport=transport,
                plugins=[MyLoggingPlugin()])
service = client.create_service( "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
                                'https://{}:8443/axl/'.format( CUCM_LOCATION ))

device_pool_data = {
    'name': DEVICE_POOL_NAME,
    'localRouteGroup': []
}

device_pool_data['localRouteGroup'].append(
    {
        'name': 'Standard Local Route Group',
        'value': STANDARD_ROUTE_GROUP_NAME
    }
)

device_pool_data['localRouteGroup'].append(
    {
        'name': 'test Local Route Group',
        'value': TEST_ROUTE_GROUP_NAME
    }
)

# the ** before line_data tells the Python function to expect
# an unspecified number of keyword/value pairs

try:
    resp = service.updateDevicePool(**device_pool_data)
except Fault as err:
    print("Zeep error: {0}".format(err))
else:
    print("updateDevicePool response:")
    print(resp)
    
