"""AXL <addAppUser> and <addPhone> sample script, using the Zeep SOAP library

Creates a CSF phone device, then creates a new Application User and associates
the new device.  Finally the Application User and phone are removed.

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
WSDL_FILE = 'schema/AXLAPI.wsdl'

# This class lets you view the incoming and outgoing http headers and XML

class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):
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

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
session.verify = False

# To enable SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( creds.USERNAME, creds.PASSWORD )

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
                                'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ))

# Create a simple phone
# Of note, this appears to be the minimum set of elements required 
# by the schema/Zeep
phone = {
        'name': 'CSFTESTPHONE',
        'product': 'Cisco Unified Client Services Framework',
        'model': 'Cisco Unified Client Services Framework',
        'class': 'Phone',
        'protocol': 'SIP',
        'protocolSide': 'User',
        'devicePoolName': 'Default',
        'commonPhoneConfigName': 'Standard Common Phone Profile',
        'locationName': 'Hub_None',
        'useTrustedRelayPoint': 'Default',
        'builtInBridgeStatus': 'Default',
        'packetCaptureMode': 'None',
        'certificateOperation': 'No Pending Operation',
        'deviceMobilityMode': 'Default'
}

# Execute the addPhone request
try:
	resp = service.addPhone( phone )
except Exception as err:
	print("\nZeep error: addPhone: {0}".format( err ) )
else:
	print( "\naddPhone response:\n" )
	print( resp )

input( '\nPress Enter to continue...' )

# Create an Application User
app_user = {
    'userid': 'testAppUser',
    'password': 'Cisco1234!',
    'presenceGroupName': 'Standard Presence Group',
    'associatedDevices': {
        'device': []
    }
}

app_user['associatedDevices']['device'].append( 'CSFTESTPHONE' )

# Execute the addAppUser request
try:
	resp = service.addAppUser( app_user )
except Exception as err:
	print("\nZeep error: addAppUser: {0}".format( err ) )
else:
	print( "\naddAppUser response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created
try:
    resp = service.removeAppUser( userid = 'testAppUser' )
except Fault as err:
    print( 'Zeep error: removeAppUser: {err}'.format( err = err ) )
else:
    print( '\nremoveAppUser response:' )
    print( resp, '\n' )

try:
    resp = service.removePhone( name = 'CSFTESTPHONE' )
except Fault as err:
    print( 'Zeep error: removePhone: {err}'.format( err = err ) )
else:
    print( '\nremovePhone response:' )
    print( resp, '\n' )








