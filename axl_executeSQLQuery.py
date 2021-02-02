"""AXL <executeSQLQuery> sample script, using the Zeep SOAP library

Creates a Call Pickup Group and associates two test Lines, then executes a SQL
query joining the numplan, pickupgrouplinemap, pickupgroup to list the DNs 
belonging to the pickup group.

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

session.verify = False

# To enabled SSL cert checking (recommended for production)
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
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )

# Create a test Call Pickup Group
call_pickup_group = {
    'pattern': '9876543210',
    'routePartitionName': None,
    'pickupNotification': 'Visual Alert',
    'pickupNotificationTimer': 6,
    'name': 'testCallPickupGroup'
}

# Execute the addCallPickupGroup request
try:
	resp = service.addCallPickupGroup( call_pickup_group )
except Fault as err:
	print("Zeep error: addCallPickupGroup: {0}".format( err ) )
else:
	print( "\naddCallPickupGroup response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create the first test Line
line = {
    'pattern': '9876543211',
    'usage': 'Device',
    'routePartitionName': None,
    'callPickupGroupName': 'testCallPickupGroup'
}

# Execute the addLine request
try:
	resp = service.addLine( line )
except Fault as err:
	print("Zeep error: addLine: {0}".format( err ) )
else:
	print( "\naddLine response:\n" )
	print( resp,"\n" )

# Create the second test Line
line[ 'pattern' ] = '9876543212'

# Execute the addLine request
try:
	resp = service.addLine( line )
except Fault as err:
	print("Zeep error: addLine: {0}".format( err ) )
else:
	print( "\naddLine response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create an object containing the raw SQL query to run
sql = '''select numplan.dnorpattern from numplan, pickupgrouplinemap, pickupgroup
            where numplan.pkid = pickupgrouplinemap.fknumplan_line and
            pickupgrouplinemap.fkpickupgroup = pickupgroup.pkid and
            pickupgroup.name = "testCallPickupGroup"'''

# Execute the executeSQLQuery request
try:
    resp = service.executeSQLQuery( sql )
except Fault as err:
    print('Zeep error: executeSQLQuery: {err}'.format( err = err ) )
else:
    print( '\nexecuteSQLQuery response:' )
    print( resp )

input( 'Press Enter to continue...' )


# Create a simple report of the SQL response
print( 'Directory Numbers belonging to testCallPickupGroup' )
print( '==================================================')

for rowXml in resp[ 'return' ][ 'row' ]:

    z = rowXml[ 0 ].text
    print( z )


# Cleanup the objects we just created
try:
    resp = service.removeLine( pattern = '9876543211', routePartitionName = None )
except Fault as err:
    print( 'Zeep error: removeLine: {err}'.format( err = err ) )
else:
    print( '\nremoveLine response:' )
    print( resp, '\n' )

try:
    resp = service.removeLine( pattern = '9876543212', routePartitionName = None )
except Fault as err:
    print( 'Zeep error: removeLine: {err}'.format( err = err ) )
else:
    print( '\nremoveLine response:' )
    print( resp, '\n' )

try:
    resp = service.removeCallPickupGroup( name = 'testCallPickupGroup' )
except Fault as err:
    print( 'Zeep error: removeCallPickupGroup: {err}'.format( err = err ) )
else:
    print( '\nremoteCallPickupGroup response:' )
    print( resp, '\n' )

