"""Reads a list of Usernames and DNs from a CSV file and replaces Description, Alerting Name, CallerID for those DNs with the Username value,
using the zeep library.
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
import csv
import urllib3
from xmlrpc.client import Fault
from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Settings, Plugin
from zeep.transports import Transport

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
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )
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


# Create a test Line
line = {
    'pattern': '1234567890',
    'description': 'Test Line',
    'usage': 'Device',
    'routePartitionName': None
}

# Execute the addLine request
try:
    resp = service.addLine( line )

except Fault as err:
    print( f'Zeep error: addLine: { err }' )

print( '\naddLine response:\n' )
print( resp,'\n' )


# Create a test phone, associating the User and Line
phone = {
    'name': '',
    'product': '',
    'model': '',
    'class': 'Phone',
    'protocol': 'SIP',
    'protocolSide': 'User',
    'devicePoolName': 'Default',
    'commonPhoneConfigName': 'Standard Common Phone Profile',
    'locationName': 'Hub_None',
    'useTrustedRelayPoint': 'Default',
    'builtInBridgeStatus': 'Default',
    'sipProfileName': 'Standard SIP Profile',
    'packetCaptureMode': 'None',
    'certificateOperation': 'No Pending Operation',
    'deviceMobilityMode': 'Default',
    'lines': {
        'line': [
            {
                'index': 1,
                'dirn': {
                    'pattern': '1234567890',
                    'routePartitionName': None
                }
            }
        ]
    }
}

device_products = [{'Product': 'Cisco 7821', 'Prefix': 'SEP12'},\
     {'Product': 'Cisco Dual Mode for Android', 'Prefix': 'BOT'},\
     {'Product':'Cisco Dual Mode for iPhone','Prefix': 'TCT'},\
     {'Product':'Cisco Unified Client Services Framework','Prefix': 'CSF'}]


# Execute the addPhone request
for product in device_products:
    try:
        phone['product'] = product['Product']
        phone['model'] = product['Product']
        phone['name'] = product['Prefix'] + '1234567890'
        resp = service.addPhone( phone )
    except Fault as err:
        print( f'Zeep error: addPhone: { err }' )

    print( '\naddPhone response:\n' )
    print( resp,'\n' )


# Create a test End User
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
    'associatedDevices': {
        'device': [
            'SEP121234567890',
            'TCT1234567890',
            'BOT1234567890',
            'CSF1234567890'
        ]
    },
    'presenceGroupName': 'Standard Presence group'
}

try:
    resp = service.addUser( end_user )

except Fault as err:
    print( f'Zeep error: addUser: { err }' )

print( '\naddUser response:\n' )
print( resp,'\n' )


try:
    f = open('./sample_data/axl_update_DN_Description_Alerting_CallerID.csv', encoding='utf-8')
except Fault as err:
    print(f'Error Reading CSV File: {err}')
with f:
    csv_reader = csv.reader(f, delimiter=',')
    for user in csv_reader:
        user_name = user[0]
        dn = user[1]
        try:
            lines =  service.listLine(searchCriteria={'pattern': dn}, returnedTags={'pattern': '', 'routePartitionName': ''})
        except Fault as err:
            print(f'Unable to search for line {dn}. {err}')
            continue

        if lines['return'] is not None:
            lines = lines['return']['line']
            for line in lines:
                pattern = line['pattern']
                partition = line['routePartitionName']['_value_1']
                try:
                    line = service.getLine(pattern = pattern, routePartitionName = partition)['return']['line']
                except Fault as err:
                    print(f'Unable to get line {pattern}/{partition}. {err}')    
                    continue
    
                try:
                    result = service.updateLine(pattern = pattern, routePartitionName = partition, description = user_name,
                        alertingName = user_name, asciiAlertingName = user_name)
                except Fault as err:
                    print(f'Unable to update line {pattern}/{partition} for user {user_name}. {err}')    
                    continue  

                if line['associatedDevices'] is not None:
                    for device in line['associatedDevices']['device']:
                        phone = service.getPhone(name = device)['return']['phone']
                        if phone['lines']['line'] is not None:
                            phone_lines = phone['lines']['line']
                            for phone_line in phone_lines:
                                if phone_line['dirn']['pattern'] == pattern and phone_line['dirn']['routePartitionName']['_value_1'] == partition:
                                    index = phone_line['index']
                                    dirn_uuid = phone_line['dirn']['uuid']
                                    try:
                                        service.updatePhone(name = device, lines={ 'line': {'index': index, 
                                            'display': user_name, 'displayAscii': user_name, 'dirn': {'pattern': pattern, 'routePartitionName': {'_value_1': partition} }}})
                                        print(f'Updated Device: {device} Pattern: {pattern}/{partition} Username: {user_name} Successfully.')
                                    except Fault as err:
                                        print(f'Unable to update line appearance (Device-Line related fields) for Device: {device} Pattern: {pattern}/{partition} with the Username: {user_name}. {err}')  
        else:
            print(f'There was no pattern matching {dn}')


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

remove_phone(['SEP121234567890', 'TCT1234567890', 'BOT1234567890', 'CSF1234567890'])
