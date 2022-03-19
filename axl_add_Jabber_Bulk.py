"""AXL adds CSF BOT TCT (Jabber Devices) for every user which is assigned as 
Owner User ID to a SEP device, using the zeep library.

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

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
import sys
import urllib3

# Edit .env file to specify your Webex site/user details
import os
from dotenv import load_dotenv
load_dotenv()

# The WSDL is a local file
WSDL_FILE = 'schema/AXLAPI.wsdl'

# Change to true to enable output of request/response headers and XML
DEBUG = False

# If you have a pem file certificate for CUCM, uncomment and define it here

#CERT = 'some.pem'

# These values should work with a DevNet sandbox
# You may need to change them if you are working with your own CUCM server



# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin( Plugin ):

    def egress( self, envelope, http_headers, operation, binding_options ):

        # Format the request body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode')

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

session = Session()

# We avoid certificate verification by default, but you can uncomment and set
# your certificate here, and comment out the False setting

#session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth( os.getenv( 'AXL_USERNAME' ), os.getenv( 'AXL_PASSWORD' ) )

# Create a Zeep transport and set a reasonable timeout value
transport = Transport( session = session, timeout = 10 )

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings( strict=False, xml_huge_tree=True )

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [ MyLoggingPlugin() ] if DEBUG else [ ]

# Create the Zeep client with the specified settings
client = Client( WSDL_FILE, settings = settings, transport = transport,
        plugins = plugin )

# service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)
service = client.create_service( '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding',
                                f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/' )



def fill_phone_info(_name, _product, _ownerUserName, _pattern, _partition, _caller_id, _busy_trigger):
    phone_info = {
        'name': _name,
        'product': _product,
        'model': _product,
        'description': f'{_ownerUserName} {_name[:3]} {_pattern} AUTO JAB',
        'class': 'Phone',
        'protocol': 'SIP',
        'protocolSide': 'User',
        'devicePoolName': 'Default',
        'locationName': 'Hub_None',
        'sipProfileName': 'Standard SIP Profile',
        'commonPhoneConfigName': xsd.SkipValue,
        'phoneTemplateName': xsd.SkipValue,
        'primaryPhoneName': xsd.SkipValue,
        'useTrustedRelayPoint': xsd.SkipValue,
        'builtInBridgeStatus': xsd.SkipValue,
        'packetCaptureMode': xsd.SkipValue,
        'certificateOperation': xsd.SkipValue,
        'deviceMobilityMode': xsd.SkipValue,
        'ownerUserName': _ownerUserName,
        'lines': {
            'line': [
                {
                    'index': 1,
                    'display': _caller_id,
                    'dirn': {
                        'pattern': _pattern,
                        'routePartitionName': _partition,
                        'busyTrigger': _busy_trigger
                        },
                        'associatedEndusers': {
                            'enduser': [
                                {
                                    'userId': _ownerUserName
                                }
                            ]    
                        }    
                }     
            ]
        }
    }
    return phone_info


jabber_products = [{'Product': 'Cisco Dual Mode for Android', 'Prefix': 'BOT'},\
     {'Product':'Cisco Dual Mode for iPhone','Prefix': 'TCT'},\
     {'Product':'Cisco Unified Client Services Framework','Prefix': 'CSF'}]
resp = service.listPhone(searchCriteria = { 'name': 'SEP%' }, returnedTags = { 'name': '', 'ownerUserName': '' })

phones_list = resp['return']['phone']
for i in phones_list:
    resp = service.getPhone(name=i['name'])
    owner_user_name = resp['return']['phone']['ownerUserName']['_value_1']
    if owner_user_name != None:
        phone = resp['return']['phone']
        line = phone['lines']['line'][0]
        pattern = line['dirn']['pattern']
        partition = line['dirn']['routePartitionName']['_value_1']
        caller_id = line['display']
        busy_trigger = line['busyTrigger']
        resp = service.getUser(userid=owner_user_name)
        devices = resp['return']['user']['associatedDevices']
        
        if devices == None:
            devices = []
            associated_devices = {'device': devices}
        else:
            associated_devices = devices

        for prod in jabber_products:
            device_name = prod['Prefix'] + pattern
            new_phone = fill_phone_info(device_name, prod['Product']\
                ,owner_user_name, pattern, partition, caller_id, busy_trigger)
            
            try:
                resp = service.addPhone(new_phone)
                associated_devices['device'].append(device_name)
            except Fault as err:
                print(f'Could Not Add {device_name} for {owner_user_name}\n{err}')
            try:
                resp = service.updateUser(userid=owner_user_name, associatedDevices=associated_devices)
            except Fault as err:
                print(f'Error for {owner_user_name} \n {associated_devices} \n{err}')
