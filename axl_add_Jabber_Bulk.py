"""AXL Creates a DN, SEP Device and End User.
Then Searches for the SEP Device (Search Criteria can be expanded to include multiple entities in result) 
and adds CSF BOT TCT (Jabber Devices) for the user which is assigned as 
Owner User ID to that SEP device(s) and enables IM and Presence for that End User, using the zeep library.

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

import os
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth

from zeep import Client, Settings, Plugin, xsd
from zeep.transports import Transport
from zeep.exceptions import Fault


# Edit .env file to specify your Webex site/user details
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



def fill_phone_info(name, product, owner_user_name, pattern, partition, caller_id, busy_trigger):
    phone_info = {
        'name': name,
        'product': product,
        'model': product,
        'description': f'{owner_user_name} {name[:3]} {pattern} AUTO',
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
        'ownerUserName': owner_user_name,
        'lines': {
            'line': [
                {
                    'index': 1,
                    'display': caller_id,
                    'dirn': {
                        'pattern': pattern,
                        'routePartitionName': partition,
                        'busyTrigger': busy_trigger
                        },
                        'associatedEndusers': {
                            'enduser': [
                                {
                                    'userId': owner_user_name
                                }
                            ]    
                        }    
                }     
            ]
        }
    }
    return phone_info


# Create a test Line
line = {
    'pattern': '1234567890',
    'description': 'Test Line',
    'usage': 'Device',
    'routePartitionName': None,
    'callForwardAll': {
        'forwardToVoiceMail': 'true'
    }
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )

print( '\naddLine response:\n' )
print( resp,'\n' )

# Create a test User
end_user = {
    'firstName': 'testFirstName',
    'lastName': 'testLastName',
    'userid': 'testUser',
    'password': 'C1sco12345',
    'pin': '123456',
    'userLocale': 'English United States',
    'associatedGroups': {
        'userGroup': [
            {
                'name': 'Standard CCM End Users',
                'userRoles': {
                    'userRole': [
                        'Standard CCM End Users',
                        'Standard CTI Enabled'
                    ]
                }
            }
        ]
    },
    'presenceGroupName': 'Standard Presence group',
    'imAndPresenceEnable': True
}

try:
    resp = service.addUser( end_user )

except Fault as err:
    print( f'Zeep error: addUser: { err }' )

print( '\naddUser response:\n' )
print( resp,'\n' )


new_phone = fill_phone_info('SEP123456789012', 'Cisco 7821', 'testUser', '1234567890', None, 'testUser', 1)
try:
    resp = service.addPhone(new_phone)
except Fault as err:
    print(f'Could Not Add SEP123456789012 for testUst \n{err}')

try:
    resp = service.updateUser(userid='testUser', associatedDevices={'device': ['SEP123456789012']})
except Fault as err:
    print(f'Error for testUser \n SEP123456789012 \n{err}')


jabber_products = [{'Product': 'Cisco Dual Mode for Android', 'Prefix': 'BOT'},\
     {'Product':'Cisco Dual Mode for iPhone','Prefix': 'TCT'},\
     {'Product':'Cisco Unified Client Services Framework','Prefix': 'CSF'}]

# You can use 'name': 'SEP%' to retrieve all SEP Phones but if you have large set of SEP Phones be caution
# Using the Search Criteria like 'name' : 'SEP1%' could reduce the search scope to avoid any issues
resp = service.listPhone(searchCriteria = { 'name': 'SEP123456789012%' }, returnedTags = { 'name': '', 'ownerUserName': '' })

phones_list = resp['return']['phone']

for i in phones_list:
    resp = service.getPhone(name=i['name'])
    phone_owner_user_name = resp['return']['phone']['ownerUserName']['_value_1']
    if phone_owner_user_name is not None:
        phone = resp['return']['phone']
        phone_line = phone['lines']['line'][0]
        phone_pattern = phone_line['dirn']['pattern']
        phone_partition = phone_line['dirn']['routePartitionName']['_value_1']
        phone_caller_id = phone_line['display']
        phone_busy_trigger = phone_line['busyTrigger']
        resp = service.getUser(userid=phone_owner_user_name)
        devices = resp['return']['user']['associatedDevices']

        if devices is None:
            devices = []
            associated_devices = {'device': devices}
        else:
            associated_devices = devices

        for prod in jabber_products:
            device_name = prod['Prefix'] + phone_pattern
            new_phone = fill_phone_info(device_name, prod['Product']\
                ,phone_owner_user_name, phone_pattern, phone_partition, phone_caller_id, phone_busy_trigger)
            
            try:
                resp = service.addPhone(new_phone)
                associated_devices['device'].append(device_name)
                resp = service.updateUser(userid=phone_owner_user_name, associatedDevices=associated_devices, imAndPresenceEnable=True)
            except Fault as err:
                print(f'Could Not Add {device_name} for {phone_owner_user_name} or Append it to Associated Devices\n{err}')
                

# Cleanup the objects we just created
input('Press Enter to start cleanup: ')

try:
    resp = service.removeUser( userid = 'testUser')
    print( '\nremoveUser response:' )
    print( resp, '\n' )
except Fault as err:
    print( f'Zeep error: removeUser: { err }' )


try:
    resp = service.removeLine( pattern = '1234567890')
    print( '\nremoveLine response:' )
    print( resp, '\n' )
except Fault as err:
    print( f'Zeep error: removeLine: { err }' )


def remove_phone(device_names):
    for device in device_names:
        try:
            resp = service.removePhone( name = device)
            print( '\nremovePhone response:' )
            print( resp, '\n' )
        except Fault as err:
            print( f'Zeep error: removePhone: { err }' )

remove_phone(['SEP123456789012', 'TCT1234567890', 'BOT1234567890', 'CSF1234567890'])
