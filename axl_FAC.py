"""AXL <addFacInfo> / <updateFacInfo>sample script, using the zeep library

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

plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin ) 

service = client.create_service( "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
                                'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ))

# Add FAC
fac_data = {
    'name': 'testFAC',
    'code': '1234',
    'authorizationLevel': '0'
}

try:
    resp = service.addFacInfo( fac_data )
except Fault as err:
    print('Zeep error: addFacInfo: {err}'.format( err = err))
else:
    print('addFacInfo response:')
    print(resp)

input( 'Press Enter to continue...')

# Update FAC
try:
    resp = service.updateFacInfo( name = 'testFAC',
        newName = 'newTestFAC',
        code = '5678',
        authorizationLevel = '1' )
except Fault as err:
    print('Zeep error: updateFacInfo: {err}'.format( err = err))
else:
    print('updateFacInfo response:')
    print(resp)

input( 'Press Enter to continue...')

# Delete FAC
try:
    resp = service.removeFacInfo( name = 'newTestFAC' )
except Fault as err:
    print('Zeep error: removeFacInfo: {err}'.format( err = err))
else:
    print('removeFacInfo response:')
    print(resp)

input( 'Press Enter to continue...')
