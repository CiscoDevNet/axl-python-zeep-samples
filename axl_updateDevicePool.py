"""AXL <updateDevicePool> sample script, using the zeep library

Description: 

Performs the following operations to create/update a Device Pool and its
sub-objects in the proper order:

<addDevicePool>
<addH323Gateway>
<addRouteGroup>
<addLocalRouteGroup>
<updateDevicePool>
<removeH323Gateway>
<removeDevicePool>
<removeLocalRouteGroup>
<removeRouteGroup>

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

# The WSDL is a local file in the project root, see README
WSDL_FILE = 'schema/AXLAPI.wsdl'

# Change to true to enable output of request/response headers and XML
DEBUG = False

# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):
        print(
'''Request
-------
Headers:
{}

Body:
{}

'''.format( http_headers, 
                etree.tostring( envelope, pretty_print = True, encoding = 'unicode' ) )
        )

    def ingress( self, envelope, http_headers, operation ):
        print( '\n' )
        print(
'''Response
-------
Headers:
{}

Body:
{}

'''.format( http_headers, 
                etree.tostring( envelope, pretty_print = True, encoding = 'unicode' ) )
        )

# This is where the meat of the application starts
# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
session.verify = False

# To enabled SSL cert checking (production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( creds.USERNAME, creds.PASSWORD )

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
                                'https://{}:8443/axl/'.format( creds.CUCM_ADDRESS ) )

# Create an object with the Device Pool fields and data
# Represents the minimal set of required fields
device_pool = {
    'name': 'testDevicePool',
    'callManagerGroupName': 'Default',
    'dateTimeSettingName': 'CMLocal',
    'regionName': 'Default',
    'srstName': 'Disable'
}

# Execute the addDevicePool request
resp = service.addDevicePool( device_pool )

print( '\naddDevicePool response:\n', resp )

input( 'Press Enter to continue...' )

# Create a H.323 Gateway device
# Represents the minimal set of required fields
h323_gateway = {
    'name': 'testH323Gateway',
    'product': 'H.323 Gateway',
    'class': 'Gateway',
    'protocol': 'H.225',
    'protocolSide': 'Network',
    'devicePoolName': 'testDevicePool',
    'locationName': 'Hub_None',
    'tunneledProtocol': 'None',
    'useTrustedRelayPoint': 'Default',
    'packetCaptureMode': 'None',
    'callingPartySelection': 'Originator',
    'callingLineIdPresentation': 'Default',
    'signalingPort': '1720',
    'calledPartyIeNumberType': 'Cisco CallManager',
    'callingPartyIeNumberType': 'Cisco CallManager',
    'calledNumberingPlan': 'Cisco CallManager',
    'callingNumberingPlan': 'Cisco CallManager'
}

# Execute the addH323Gateway request
resp = service.addH323Gateway( h323_gateway )

print( '\naddH323Gateway response:\n', resp )

input( 'Press Enter to continue...' )

# Create a Route Group
# members is a field, while member is the array
route_group = {
    'name': 'testRouteGroup',
    'distributionAlgorithm': 'Circular',
    'members': {
        'member': []
    }
}

# Add the H323 Gateway to the members->member array
route_group[ 'members' ][ 'member' ].append(
    {
        'deviceName': 'testH323Gateway',
        'port': 0,
        'deviceSelectionOrder': 1
    }
)

# Execute the addRouteGroup request
resp = service.addRouteGroup( route_group )

print( '\naddRouteGroup response:\n', resp )

input( 'Press Enter to continue...' )

# Create a Local Route Group
local_route_group = {
    'name': 'testLocalRouteGroup',
    'description': 'Test Local Route Group'
}

# Execute the addLocalRouteGroup request
resp = service.addLocalRouteGroup( local_route_group )

print( '\naddLocalRouteGroup response:\n', resp )

input( 'Press Enter to continue...' )

# Now, update the Device Pool to specify Local Route Groups

# Create an array for holding Local Route Groups
localRouteGroup = []

# Add two entries to the localRouteGroup array
localRouteGroup.append(
    {
        'name': 'Standard Local Route Group',
        'value': 'testRouteGroup'
    }
)

localRouteGroup.append(
    {
        'name': 'testLocalRouteGroup',
        'value': 'testRouteGroup'
    }
)

# Execute the updateDevicePool request
resp = service.updateDevicePool( name = 'testDevicePool', localRouteGroup = localRouteGroup )

print( '\nupdateDevicePool response:\n', resp )
    
input( 'Press Enter to continue...' )

# Cleanup the objects we just created
resp = service.removeH323Gateway( name = 'testH323Gateway' )

print( '\nremoveH323Gateway response:\n', resp )

resp = service.removeDevicePool( name = 'testDevicePool' )

print( '\nremoveDevicePool response:\n', resp )

resp = service.removeRouteGroup( name = 'testRouteGroup' )

print( '\nremoveRouteGroup response:\n', resp )

resp = service.removeLocalRouteGroup( name = 'testLocalRouteGroup' )

print( '\nremoveLocalRouteGroup response:\n', resp )
