"""AXL <addUcService> and <executeSQLUpdate> sample script, using the Zeep SOAP library

Creates a set of UC Services of type Video Conference Scheduling Portal, and an
empty Service Profile.   Then executes a SQL update to associate the 
primary/secondary Services to the Profile.

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

# Create UC Service #1
uc_service = {
    'serviceType': 'Video Conference Scheduling Portal',
    'productType': 'Telepresence Management System',
    'name': 'testConferenceSchedulingPortal1',
    'hostnameorip': '10.10.10.101',
    'port': 80,
    'protocol': 'http',
    'ucServiceXml': '<TmsPortalUrl>http://10.10.10.101/</TmsPortalUrl>'
}

# Execute the addUcService request
try:
	resp = service.addUcService( uc_service )
except Fault as err:
	print("Zeep error: addUcService: {0}".format( err ) )
else:
	print( "\naddUcService response:\n" )
	print( resp,"\n" )

# Store the returned unique ID, removing braces and converting to lowercase
ucServiceId_1 = resp['return'].strip('{}').lower()

input( 'Press Enter to continue...' )

# Create UC Service #2
uc_service = {
    'serviceType': 'Video Conference Scheduling Portal',
    'productType': 'Telepresence Management System',
    'name': 'testConferenceSchedulingPortal2',
    'hostnameorip': '10.10.10.102',
    'port': 80,
    'protocol': 'http',
    'ucServiceXml': '<TmsPortalUrl>http://10.10.10.102/</TmsPortalUrl>'
}

# Execute the addUcService request
try:
	resp = service.addUcService( uc_service )
except Fault as err:
	print("Zeep error: addUcService: {0}".format( err ) )
else:
	print( "\naddUcService response:\n" )
	print( resp,"\n" )

# Store the returned unique ID, removing braces and converting to lowercase
ucServiceId_2 = resp['return'].strip('{}').lower()

input( 'Press Enter to continue...' )

# Create the UC Service Profile
uc_service_profile = {
    'name': 'testServiceProfile',
    'isDefault': False,
    'serviceProfileInfos': {
        'serviceProfileInfo': []
    }
}

# Normally you would include specific profile type primary/secondary/tertiary
# services as below.  However this is not working as of this writing due to CSCvq97982.
# Subsequently we'll show how to associate these via executeSQLUpdate

# uc_service_profile['serviceProfileInfos']['serviceProfileInfo'].append(
#     {
#         'profileName': 'Video Conference Scheduling Portal Profile',
#         'primary': 'testConferenceSchedulingPortal1'
#     }
# )

# Execute the addServiceProfile request
try:
	resp = service.addServiceProfile( uc_service_profile )
except Fault as err:
	print("Zeep error: addServiceProfile: {0}".format( err ) )
else:
	print( "\naddServiceProfile response:\n" )
	print( resp,"\n" )

# Store the returned unique ID, removing braces and converting to lowercase
ucServiceProfileId = resp['return'].strip('{}').lower()

input( 'Press Enter to continue...' )

# Create an object containing the raw SQL update to run
sql = '''UPDATE ucserviceprofiledetail SET fkucservice_1 = "{ucServiceId_1}", 
    fkucservice_2 = "{ukServiceId_2}"
    WHERE fkucserviceprofile = "{ucServiceProfileId}" AND
    tkucservice = 41'''.format( 
        ucServiceId_1 = ucServiceId_1,
        ukServiceId_2 = ucServiceId_2,
        ucServiceProfileId = ucServiceProfileId)

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
    resp = service.removeServiceProfile( name = 'testServiceProfile' )
except Fault as err:
    print( 'Zeep error: removeServiceProfile: {err}'.format( err = err ) )
else:
    print( '\nremoveServiceProfile response:' )
    print( resp, '\n' )

try:
    resp = service.removeUcService( name = 'testConferenceSchedulingPortal1' )
except Fault as err:
    print( 'Zeep error: removeUcService: {err}'.format( err = err ) )
else:
    print( '\nremoveUcService response:' )
    print( resp, '\n' )

try:
    resp = service.removeUcService( name = 'testConferenceSchedulingPortal2' )
except Fault as err:
    print( 'Zeep error: removeUcService: {err}'.format( err = err ) )
else:
    print( '\nremoveUcService response:' )
    print( resp, '\n' )







