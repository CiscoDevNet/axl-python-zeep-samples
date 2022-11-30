"""AXL <listRegistrationDynamic> sample script, using the Zeep SOAP library

Retrieves real-time registration info for devices via <listRegistrationDynamic>,
and prints a simple report.

Copyright (c) 2022 Cisco and/or its affiliates.
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
import sys
import urllib3

from zeep import Client, Settings, Plugin, xsd
from zeep import xsd
from zeep.transports import Transport
from zeep.exceptions import Fault

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

# To enable SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows Zeep to parse imperfect XML
settings = Settings( strict = False, xml_huge_tree = True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else []

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# Create an object to indicate which lists tags to return

returnedTags = {
    'device': xsd.Nil,
    'lastKnownIpAddress': xsd.Nil,
    'lastKnownUcm': xsd.Nil,
    'lastSeen': xsd.Nil,
    'risStatus': xsd.Nil
}

# Execute listRegistrationDynamic request
try:
    resp = service.listRegistrationDynamic( searchCriteria = { 'device': '%' }, returnedTags = returnedTags )
except Exception as err:
    print( f'\nZeep error: listRegistrationDynamic: { err }' )
    sys.exit( 1 )

print( f'DeviceName{ 40 * " " } Last Known IP{ 3 * " " } Last Known UCM{ 2 * " " } Last Seen{ 2 * " " } Status' )
print( f'{ 50 * "-" } { 16 * "-" } { 16 * "-" } { 11 * "-" } { 19 * "-" }' )

# Loop through the dictionary of registrationDynamic entries and retrieve/print individual device details
for device in resp[ 'return' ][ 'registrationDynamic' ]:

    print( device[ 'device' ]._value_1.ljust( 50, ' ' ),
        ( device[ 'lastKnownIpAddress' ] if device[ 'lastKnownIpAddress' ] else '' ).ljust( 16, ' ' ),
        ( device[ 'lastKnownUcm' ] if device[ 'lastKnownUcm' ] else '' ).ljust( 16, ' ' ),
        ( device[ 'lastSeen' ] if device[ 'lastSeen' ] else '' ).ljust( 11, ' ' ),
        ( device[ 'risStatus' ] if device[ 'risStatus' ] else '' ).ljust( 19, ' ' )
    )




