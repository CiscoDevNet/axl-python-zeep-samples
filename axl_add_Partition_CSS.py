"""AXL <addRoutePartition> and <addCss> sample script, using the zeep library

Copyright (c) 2020 Cisco and/or its affiliates.
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
import sys
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# Change to true to enable output of request/response headers and XML
DEBUG = False

# The WSDL is a local file in the working directory, see README
WSDL_FILE = 'schema/AXLAPI.wsdl'

# The below Partions and CSSs will be created

PARTITION1_NAME = 'testPartition1'
PARTITION2_NAME = 'testPartition2'
CSS_NAME = 'newCss'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# This is where the meat of the application starts
# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )  

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# Add testPartition1
partition_data = {
    'name': PARTITION1_NAME
}

try:
    resp = service.addRoutePartition( partition_data )
except Fault as err:
    print( 'Zeep error: addRoutePartition (1 of 2): {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\naddRoutePartition (1 of 2) response:' )
print( resp, '\n' )

input( 'Press Enter to continue...' )

# Add testPartition2
partition_data = {
    'name': PARTITION2_NAME
}
try:
    resp = service.addRoutePartition( partition_data )
except Fault as err:
    print( 'Zeep error: addRoutePartition (2 of 2): {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\naddRoutePartition (2 of 2) response:' )
print( resp )

input( 'Press Enter to continue...' )
print()

# Add testCss
css_data = {
    'name': CSS_NAME,
    'members': { 
        'member': [ ] 
    }
} 

css_data[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': PARTITION1_NAME,
            'index': '1'
    }
)

css_data[ 'members' ][ 'member' ].append(
    {
            'routePartitionName': PARTITION2_NAME,
            'index': '2'
    }
)

try:
    resp = service.addCss( css_data )
except Fault as err:
    print( 'Zeep error: addCss: {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\naddCss response:' )
print( resp )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created

try:
    resp = service.removeCss( name = CSS_NAME )
except Fault as err:
    print( 'Zeep error: removeCss: {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremoveCss response:' )
print( resp )

try:
    resp = service.removeRoutePartition( name = PARTITION1_NAME )
except Fault as err:
    print( 'Zeep error: remoteRoutePartition (1 of 2): {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremoveRoutePartition (1 or 2) response:' )
print( resp )

try:
    resp = service.removeRoutePartition( name = PARTITION2_NAME )
except Fault as err:
    print( 'Zeep error: remoteRoutePartition (2 of 2): {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremoveRoutePartition (2 or 2) response:' )
print( resp )
