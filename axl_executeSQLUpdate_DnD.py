"""AXL <addPhone> and <executeSQLUpdate> sample script, using the Zeep SOAP library

Creates an enduser, line and Jabber for Android BOT phone and associates the three.
Then sets Do-not-Disturb on the phone via <executeSqlUpdate> to the CUCM 'dnddynamic'
 table.  Finally, all objects are deleted.

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

line = {
    'pattern': '9876543211',
    'usage': 'Device',
    'routePartitionName': None
}

# Execute the addLine request
try:
	resp = service.addLine( line )
except Fault as err:
	print("Zeep error: addLine: {0}".format( err ) )
else:
	print( "\naddLine response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create a simple phone
# Of note, this appears to be the minimum set of elements required 
# by the schema/Zeep
phone = {
        'name': 'BOTTESTPHONE',
        'product': 'Cisco Dual Mode for Android',
        'model': 'Cisco Dual Mode for Android',
        'class': 'Phone',
        'protocol': 'SIP',
        'protocolSide': 'User',
        'devicePoolName': 'Default',
        'lines': { 
            'line': [
                {
                    'dirn': {
                        'pattern': '9876543211',
                        'routePartitionName': ''
                    },
                    'index': 1
                }
            ]
        },
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

deviceId = resp['return'].strip('{}').lower()

input( '\nPress Enter to continue...' )

# Create an End User
end_user = {
    'userid': 'testEndUser',
    'lastName': 'testEndUser',
    'password': 'Cisco1234!',
    'presenceGroupName': 'Standard Presence Group',
    'associatedDevices': {
        'device': [ 'BOTTESTPHONE' ]
    },
    'associatedGroups': {
        'userGroup': [
            { 'name': 'Standard CCM End Users'}
        ]
    },
    'imAndPresenceEnable': True
}

# Execute the addUser request
try:
	resp = service.addUser( end_user )
except Exception as err:
	print("\nZeep error: addUser: {0}".format( err ) )
else:
	print( "\naddUser response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create an object containing the raw SQL update to run
sql = f'UPDATE dnddynamic SET dndstatus = "t" where fkdevice="{deviceId}"'

# Execute the executeSQLQuery request
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print('Zeep error: executeSQLUpdate: {err}'.format( err = err ) )
else:
    print( 'executeSQLUpdate response:' )
    print( resp )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created

try:
    resp = service.removeUser( userid = 'testEndUser' )
except Fault as err:
    print( 'Zeep error: removeUser: {err}'.format( err = err ) )
else:
    print( '\nremoveUser response:' )
    print( resp, '\n' )

try:
    resp = service.removePhone( name = 'BOTTESTPHONE' )
except Fault as err:
    print( 'Zeep error: removePhone: {err}'.format( err = err ) )
else:
    print( '\nremovePhone response:' )
    print( resp, '\n' )

try:
    resp = service.removeLine( pattern = '9876543211', routePartitionName = None )
except Fault as err:
    print( 'Zeep error: removeLine: {err}'.format( err = err ) )
else:
    print( '\nremoveLine response:' )
    print( resp, '\n' )






