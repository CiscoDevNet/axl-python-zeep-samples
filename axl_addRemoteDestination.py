"""AXL <addRemoteDestination> sample script, using the Zeep SOAP library

Creates an EndUser, and associates a new Remote Destination Profile, 
then adds a Remote Destination.

Install Python 3.7
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
# import requests
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
        'https://{cucm}:8443/axl/'.format( cucm = creds.CUCM_ADDRESS ),
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







