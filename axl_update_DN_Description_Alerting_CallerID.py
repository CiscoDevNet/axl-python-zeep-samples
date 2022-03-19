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


from lxml import etree
from requests import Session
from requests.auth import HTTPBasicAuth
import httpx

from zeep import Client, Settings, Plugin, xsd, AsyncClient
from zeep.transports import Transport, AsyncTransport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
import sys
import urllib3
import csv

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

"""
users.csv file should be place into the same directory that this Python file exists, 
or the directory prefix should be added below.
the format of csv file is: 'username,dn'
"""

with open('users.csv') as f:
    csv_reader = csv.reader(f, delimiter=',')
    for user in csv_reader:
        user_name = user[0]
        dn = user[1]
        lines =  service.listLine(searchCriteria={'pattern': dn}, returnedTags={'pattern': '', 'routePartitionName': ''})
        if lines['return'] != None:
            lines = lines['return']['line']
            for line in lines:
                pattern = line['pattern']
                partition = line['routePartitionName']['_value_1']
                line = service.getLine(pattern = pattern, routePartitionName = partition)['return']['line']
                result = service.updateLine(pattern = pattern, routePartitionName = partition, description = user_name,
                    alertingName = user_name, asciiAlertingName = user_name)
                if line['associatedDevices'] != None:
                    for device in line['associatedDevices']['device']:
                        phone = service.getPhone(name = device)['return']['phone']
                        if phone['lines']['line'] != None:
                            phone_lines = phone['lines']['line']
                            for phone_line in phone_lines:
                                if phone_line['dirn']['pattern'] == pattern and phone_line['dirn']['routePartitionName']['_value_1'] == partition:
                                    index = phone_line['index']
                                    dirn_uuid = phone_line['dirn']['uuid']
                                    service.updatePhone(name = device, lines={ 'line': {'index': index,
                                        'display': user_name, 'displayAscii': user_name,
                                         'dirn': {'pattern': pattern, 'routePartitionName': {'_value_1': partition} }}})
