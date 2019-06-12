"""AXL <addRoutePartition> and <addCss> sample script, using the zeep library

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

# Configure CUCM location and AXL credentials in creds.py
import creds

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'AXLAPI.wsdl'

# The below Partions and CSSs will be created

PARTITION1_NAME = 'testPartition1'
PARTITION2_NAME = 'testPartition2'
CSS_NAME = 'newCss'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin(Plugin):

    def egress(self, envelope, http_headers, operation, binding_options):
        print(
'''Request
-------
Headers:
{headers}

Body:
{xml}

'''.format( headers = http_headers, 
            xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode') )
        )

    def ingress( self, envelope, http_headers, operation ):
        print('\n')
        print(
'''Response
-------
Headers:
{headers}

Body:
{xml}

'''.format( headers = http_headers, 
            xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode') )
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

session.auth = HTTPBasicAuth(creds.AXL_USERNAME, creds.AXL_PASSWORD)

transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

if DEBUG:
    client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = [MyLoggingPlugin() ] )
else:
      client = Client( WSDL_FILE, settings = settings, transport = transport )  

service = client.create_service( "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
                                'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ))

# Add testPartition1
partition_data = {
    'name': PARTITION1_NAME
}

try:
    resp = service.addRoutePartition( partition_data )
except Fault as err:
    print('Zeep error: addRoutePartition (1 of 2): {err}'.format( err = err))
else:
    print('addRoutePartition (1 of 2) response:')
    print(resp)

input( 'Press Enter to continue...')

# # Add testPartition2
partition_data = {
    'name': PARTITION2_NAME
}
try:
    resp = service.addRoutePartition( partition_data )
except Fault as err:
    print('Zeep error: addRoutePartition (2 of 2): {err}'.format( err = err))
else:
    print('addRoutePartition (2 of 2) response:')
    print(resp)

input( 'Press Enter to continue...')

# Add testCss
css_data = {
    'name': CSS_NAME,
    'members': { 'member': [ ] }
}

css_data['members']['member'].append(
    {
            'routePartitionName': PARTITION1_NAME,
            'index': '1'
    } )

css_data['members']['member'].append(
    {
            'routePartitionName': PARTITION2_NAME,
            'index': '2'
    } )

try:
    resp = service.addCss( css_data )
except Fault as err:
    print('Zeep error: addCss: {err}'.format( err = err))
else:
    print('addCss response:')
    print(resp)

input( 'Press Enter to continue...')

# Cleanup the objects we just created

try:
    resp = service.removeCss( name = CSS_NAME )
except Fault as err:
    print('Zeep error: removeCss: {err}'.format( err = err))
else:
    print('removeCss response:')
    print(resp)

try:
    resp = service.removeRoutePartition( name = PARTITION1_NAME )
except Fault as err:
    print('Zeep error: remoteRoutePartition (1 of 2): {err}'.format( err = err))
else:
    print('removeRoutePartition (1 or 2) response:')
    print(resp)

try:
    resp = service.removeRoutePartition( name = PARTITION2_NAME )
except Fault as err:
    print('Zeep error: remoteRoutePartition (2 of 2): {err}'.format( err = err))
else:
    print('removeRoutePartition (2 or 2) response:')
    print(resp)
