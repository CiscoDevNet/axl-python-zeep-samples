'''AXL <addGateway>, <addGatewayEndpointAnalogAccess> sample script, using the Zeep SOAP library

Creates a VG310 MGCP gateway with unit VG-2VWIC-MBRD and subunit 24FXS.
Then adds a new analog/POTS port/line to the subunit  Finally all created
objects are deleted.

Copyright (c) 2020 Cisco and/or its affiliates.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the 'Software'), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

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

        print( f'\nRequest\n-------\nHeaders:\n{ http_headers }\n\nBody:\n{ xml }' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode' )

        print( f'\nResponse\n-------\nHeaders:\n{ http_headers }\n\nBody:\n{ xml }' )

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

# Create an gateway object specifying VG310 MGCP gateway with 
#   VG-2VWIC-MBRD unit and 24FXS subunit
domain = 'testVG310'
unit = 0
subunit = 0
gateway = {
    'domainName': domain,
    'product': 'VG310',
    'protocol': 'MGCP',
    'callManagerGroupName': 'Default',
    'units': {
        'unit': [
            {
                'index': unit,
                'product': 'VG-2VWIC-MBRD',
                'subunits': {
                    'subunit': [
                        {
                            'index': subunit,
                            'product': '24FXS',
                            'beginPort': 0
                        }
                    ]
                }
            }
        ]
    }
}

# To add vendorConfig items, create lxml Element objects and append to 
# an array named vendorConfig, a child element under <units>
ModemPassthrough = etree.Element( 'ModemPassthrough' )
ModemPassthrough.text = 'Disable'
T38FaxRelay = etree.Element( 'T38FaxRelay' )
T38FaxRelay.text = 'Enable'
DtmfRelay = etree.Element( 'DtmfRelay' )
DtmfRelay.text = 'NTE-CA'

# Append each top-level element to an array
vendorConfig = []
vendorConfig.append( ModemPassthrough )
vendorConfig.append( T38FaxRelay )
vendorConfig.append( DtmfRelay )

# Create a Zeep xsd type object of type XVendorConfig from the client object
xvcType = client.get_type( 'ns0:XVendorConfig' )

# Use the XVendorConfig type object to create a vendorConfig object
#   using the array of vendorConfig elements from above, and set as
#   phone.vendorConfig

gateway[ 'vendorConfig' ] = xvcType( vendorConfig )

# Execute the addGateway request
try:
    resp = service.addGateway( gateway )

except Fault as err:
    print( f'Zeep error: addGateway: { err }' )
    sys.exit( 1 )

print( '\naddGateway response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# Create a line which will be added to the gateway port
line = {
    'pattern': '9876543210',
    'description': 'Test Line',
    'usage': 'Device',
    'routePartitionName': None
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )
    sys.exit( 1 )

print( '\naddLine response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# Create a gateway analog access endpoint object
# This should be close to the minimum possible fields
portName = f'AALN/S{ unit }/SU{ subunit }/0@{ domain }'
endpoint = {
    'domainName': domain,
    'unit': unit,
    'subunit': subunit,
    'endpoint': {
        'index': 0,
        'name': portName,
        'product': 'Cisco MGCP FXS Port',
        'class': 'Gateway',
        'protocol': 'Analog Access',
        'protocolSide': 'User',
        'devicePoolName': 'Default',
        'locationName': 'Hub_None',
        'port': {
            'portNumber': 1,
            'callerIdEnable': False,
            'callingPartySelection': 'Originator',
            'expectedDigits': 10,
            'sigDigits': {
                "_value_1": 10,
                "enable": False
            },
            'lines': {
                'line': [
                    {
                        'index': 1,
                        'dirn': {
                            'pattern': '9876543210',
                            'routePartitionName': None
                        }
                    }
                ]
            },
            'presentationBit': 'Allowed',
            'silenceSuppressionThreshold': 'Disable',
            'smdiPortNumber': 2048,
            'trunk': 'POTS',
            'trunkDirection': 'Bothways',
            'trunkLevel': 'ONS',
            'trunkPadRx': 'NoDbPadding',
            'trunkPadTx': 'NoDbPadding',
            'timer1': 200,
            'timer2': 0,
            'timer3': 100,
            'timer4': 1000,
            'timer5': 0,
            'timer6': 0
        },
        'trunkSelectionOrder': 'Top Down'
    }
}

# Execute the addGatewayEndpointAnalogAccess request
try:
    resp = service.addGatewayEndpointAnalogAccess( endpoint )

except Fault as err:
    print( f'Zeep error: addGatewayEndpointAnalogAccess: { err }' )
    sys.exit( 1 )

print( '\naddGatewayEndpointAnalogAccess response:\n' )
print( resp,'\n' )

input( 'Press Enter to continue...' )

# Cleanup the objects we just created

try:
    resp = service.removeGatewayEndpointAnalogAccess( name = portName )
except Fault as err:
    print( f'Zeep error: removeGatewayEndpointAnalogAccess: { err }' )
    sys.exit( 1 )

print( '\nremoveGatewayEndpointAnalogAccess response:' )
print( resp, '\n' )

try:
    resp = service.removeLine( pattern = '9876543210', routePartitionName = None )
except Fault as err:
    print( f'Zeep error: removeLine: { err }' )
    sys.exit( 1 )

print( '\nremoveLine response:' )
print( resp, '\n' )

try:
    resp = service.removeGateway( domainName = 'testVG310' )
except Fault as err:
    print( f'Zeep error: removeGateway: { err }' )
    sys.exit( 1 )

print( '\nremoveGateway response:' )
print( resp, '\n' )








