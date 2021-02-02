"""AXL addDevicePool/updateDevicePool with new Media Resource Group List
sample script, using the Zeep SOAP library

Creates a new Device Pool, then creates a new Media Resource Group List and
updates the Device Pool.

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

from zeep import Client, Settings, Plugin, xsd
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

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# Create a test Device Pool
device_pool = {
    'name': 'testDevicePool',
    'dateTimeSettingName': 'CMLocal',
    'callManagerGroupName': 'Default',
    'mediaResourceListName': None,
    'regionName': 'Default',
    'srstName': 'Disable',
    'aarNeighborhoodName': None,
    'localRouteGroup': None
}

# Execute the addDevicePool request
try:
    resp = service.addDevicePool( device_pool )
except Fault as err:
    print( f'Zeep error: addDevicePool: { err }' )
    sys.exit( 1 )

print( '\naddDevicePool response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# create a test Media Resource Group List
# xsd.SkipValue lets you ommit the (otherwise schema required)
# members field
mrgl = {
    'name': 'testMediaResourceGroupList',
    'members': xsd.SkipValue
}

# Execute the addMediaResourceList request
try:
    resp = service.addMediaResourceList( mrgl )
except Fault as err:
    print( f'Zeep error: addMediaResourceList: { err }' )
    sys.exit( 1 )

print( '\naddMediaResourceList response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# Execute the updateDevicePool request
try:
    resp = service.updateDevicePool( 
        name = 'testDevicePool',
        mediaResourceListName = 'testMediaResourceGroupList'
        )
except Fault as err:
    print( f'Zeep error: updateDevicePool: { err }' )
    sys.exit( 1 )

print( '\nupdateDevicePool response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created
try:
    resp = service.removeDevicePool( name = 'testDevicePool')
except Fault as err:
    print( f'Zeep error: removeDevicePool: { err }' )
    sys.exit( 1 )

print( '\nremoveDevicePool response:' )
print( resp, '\n' )

try:
    resp = service.removeMediaResourceList( name = 'testMediaResourceGroupList' )
except Fault as err:
    print( f'Zeep error: removeMediaResourceList: { err }' )
    sys.exit( 1 )

print( '\nremoveMediaResourceList response:' )
print( resp, '\n' )

