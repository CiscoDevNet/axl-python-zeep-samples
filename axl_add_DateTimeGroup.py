"""AXL <addPhoneNtp> and <addDateTimeGroup> sample script, using the Zeep SOAP library

Creates a two Phone NTP References, then creates a new Date Time Group using the NTP
References.  Finally the NTP References and Date Time Group are removed.

Copyright (c) 2021 Cisco and/or its affiliates.
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

from zeep import Client, Settings, Plugin
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
                                f'https://{os.getenv("CUCM_ADDRESS")}:8443/axl/' )

# Create a Phone NTP Reference
#   Note: mode can only be Directed Broadcast
ntpReference = {
        'ipAddress': '10.255.255.250',
        'ipv6Address': '',
        'mode': 'Directed Broadcast'
}

# Execute the addPhoneNtp request
try:
    resp = service.addPhoneNtp( ntpReference )
except Exception as err:
    print( f'\nZeep error: addPhoneNtp #1: { err }' )
    sys.exit( 1 )

print( '\naddPhoneNtp #1 response:\n' )
print( resp )

input( '\nPress Enter to continue...' )

# Create a second Phone NTP Reference
ntpReference = {
        'ipAddress': '10.255.255.251',
        'ipv6Address': '',
        'mode': 'Directed Broadcast'
}

# Execute the addPhoneNtp request
try:
    resp = service.addPhoneNtp( ntpReference )
except Exception as err:
    print( f'\nZeep error: addPhoneNtp #2: { err }' )
    sys.exit( 1 )

print( '\naddPhoneNtp #2 response:\n' )
print( resp )

input( '\nPress Enter to continue...' )

# Create an Date Time Group object
dateTimeGroup = {
    'name': 'testDateTimeGroup',
    'timeZone': 'America/Denver',
    'separator': '/',
    'dateformat': 'D/M/Y',
    'timeFormat': '12-hour',
    'phoneNtpReferences': {
        'selectedPhoneNtpReference': []
    }
}

dateTimeGroup['phoneNtpReferences']['selectedPhoneNtpReference'].append( { 'phoneNtpName': '10.255.255.250', 'selectionOrder': 0 } )
dateTimeGroup['phoneNtpReferences']['selectedPhoneNtpReference'].append( { 'phoneNtpName': '10.255.255.251', 'selectionOrder': 1 } )

# Execute the addDateTimeGroup request
try:
    resp = service.addDateTimeGroup( dateTimeGroup )
except Exception as err:
    print("\nZeep error: addDateTimeGroup: {0}".format( err ) )
    sys.exit( 1 )

print( "\naddDateTimeGroup addDateTimeGroup:\n" )
print( resp,"\n" )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created
try:
    resp = service.removePhoneNtp( ipAddress = '10.255.255.250', ipv6Address = ''  )
except Fault as err:
    print( 'Zeep error: removePhoneNtp #1: {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremovePhoneNtp #1 response:' )
print( resp, '\n' )

try:
    resp = service.removePhoneNtp( ipAddress = '10.255.255.251', ipv6Address = '' )
except Fault as err:
    print( 'Zeep error: removePhoneNtp #2: {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremovePhoneNtp #2 response:' )
print( resp, '\n' )

try:
    resp = service.removeDateTimeGroup( name = 'testDateTimeGroup' )
except Fault as err:
    print( 'Zeep error: removeDateTimeGroup: {err}'.format( err = err ) )
    sys.exit( 1 )

print( '\nremoveDateTimeGroup response:' )
print( resp, '\n' )








