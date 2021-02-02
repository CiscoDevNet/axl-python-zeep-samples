"""AXL <addRemoteDestination> sample script, using the Zeep SOAP library

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
# import requests
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

# Create an End User
end_user = {
    'lastName': 'testEndUser',
    'userid': 'testEndUser',
    'presenceGroupName': 'Standard Presence Group',
    'enableMobility': True
}

# Execute the addUser request
try:
	resp = service.addUser( end_user )
except Fault as err:
	print("Zeep error: addUser: {0}".format( err ) )
else:
	print( "\naddUser response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create and associate a Remote Destination Profile
remote_destination_profile = {
    'name': 'testRemoteDestinationProfile',
    'product': 'Remote Destination Profile',
    'class': 'Remote Destination Profile',
    'protocol': 'Remote Destination',
    'protocolSide': 'User',
    'devicePoolName': 'Default',
    'callInfoPrivacyStatus': 'Default',
    'userId': 'testEndUser'
}

# Execute the addRemoteDestinationProfile request
try:
    resp = service.addRemoteDestinationProfile( remote_destination_profile )
except Fault as err:
	print("Zeep error: addRemoteDestinationProfile: {0}".format( err ) )
else:
	print( "\naddRemoteDestinationProfile response:\n" )
	print( resp,"\n" )

input( 'Press Enter to continue...' )

# Create a Remote Destination
remote_destination = {
    'name': 'testRemoteDestination',
    'destination': '4055551212',
    'answerTooSoonTimer': 1500,
    'answerTooLateTimer': 19000,
    'delayBeforeRingingCell': 4000,
    'ownerUserId': 'testEndUser',
    'enableUnifiedMobility': True,
    'remoteDestinationProfileName': 'testRemoteDestinationProfile',
    'isMobilePhone': True,
    'enableMobileConnect': True
}

# Due to an issue with the AXL schema vs. implementation (11.5/12.5 - CSCvq98025)
# we have to remove the nil <dualModeDeviceName> element Zeep creates 
# via the following lines

# Use the Zeep service to create an XML object of the request - don't send
node = client.create_message( service, 'addRemoteDestination', remoteDestination = remote_destination)

# Remove the dualModeDeviceName element
for element in node.xpath("//dualModeDeviceName"):
  element.getparent().remove( element )

# Execute the addRemoteDestination request
# This has to be done a little differently since we want to send a custom payload
try:
    resp = transport.post_xml(
        f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/',
        envelope = node,
        headers = None
    )
except Fault as err:
	print("Zeep error: addRemoteDestination: {0}".format( err ) )
else:
	print( "\naddRemoteDestination response:\n" )
	print( resp.text,"\n" )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created
try:
    # removeRemoteDestination uses the destination vs the name
    resp = service.removeRemoteDestination( destination = '4055551212' )
except Fault as err:
    print( 'Zeep error: removeRemoteDestination: {err}'.format( err = err ) )
else:
    print( '\nremoveRemoteDestination response:' )
    print( resp, '\n' )

try:
    resp = service.removeRemoteDestinationProfile( name = 'testRemoteDestinationProfile' )
except Fault as err:
    print( 'Zeep error: remoteRemoveDestinationProfile: {err}'.format( err = err ) )
else:
    print( '\nremoveRemoteDestinationProfile response:' )
    print( resp, '\n' )

try:
    resp = service.removeUser( userid = 'testEndUser' )
except Fault as err:
    print( 'Zeep error: removeUser: {err}'.format( err = err ) )
else:
    print( '\nremoveUser response:' )
    print( resp, '\n' )







