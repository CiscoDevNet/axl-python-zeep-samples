"""AXL <listChange> sample script, using the Zeep SOAP library

Demonstrates usage of the AXL 'Data Change Notification' feature to 
continuosly monitor and display incremental changes to the CUCM
configuration database.

https://developer.cisco.com/docs/axl/#!axl-developer-guide/data-change-notification

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
import requests
from requests import Session
from requests.auth import HTTPBasicAuth
import time

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
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode' )

        print( f'\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

    def ingress( self, envelope, http_headers, operation ):

        # Format the response body as pretty printed XML
        xml = etree.tostring( envelope, pretty_print = True, encoding = 'unicode' )

        print( f'\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}' )

# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings( urllib3.exceptions.InsecureRequestWarning )

# This trick disables insecure request warnings, when not verifying certs
requests.packages.urllib3.disable_warnings( )

# To enable SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth( os.getenv('AXL_USERNAME'), os.getenv('AXL_PASSWORD') )

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
                                f'https://{os.getenv("CUCM_ADDRESS")}:8443/axl/' )

# Make the initial listChange request.
# No <startChange> or <objectList> provided so we get the
# first/last/queue baseline data

# Execute the listChange request
try:
    resp = service.listChange(  )

except Exception as err:
    print( f'\nZeep error: initial listChange: { err }' )
    sys.exit( 1 )

print( )
print( 'Initial listChange response:' )
print( )
print( resp )

# Store the queueId for our change list and the highest change Id
queueId = resp.queueInfo.queueId
nextStartChangeId = resp.queueInfo.nextStartChangeId

print( )
input( 'Press Enter to continue...' )

print( )
print( 'Starting loop to monitor changes...' )
print('(Press Ctrl+C to exit)')
print( )
print( f'Action doGet? Type{16 * " "} UUID{32 * " "} Field{10 * " "} Value' )
print( f'{6 * "-"} {6 * "-"} {20 * "-"} {36 * "-"} {15 * "-"} {15 * "-"}' )

# Translation dictionary for action descriptions
actions = {
    'a': 'Add',
    'u': 'Update',
    'r': 'Remove'
}

# Start the infinite loop to check for new changes every 10 sec
while True:

    # Zeep way to define an element like: 
    # <startChangeId queueId='foo'>bar</startChangeId>
    startChangeId = {
        'queueId': queueId,
        '_value_1': nextStartChangeId
    }

    # Execute the listChange request
    try:
        resp = service.listChange( startChangeId )

    except Exception as err:
        print( f'\nZeep error: polling listChange: { err }' )
        sys.exit(1)

    # If any changes were retrieved...
    if resp.changes:

        # Loop through each change in the changes list
        for change in resp.changes.change:

            # If there are any items in the changedTags list...
            if change.changedTags:

                # Loop through each changedTag
                for x in range( len( change.changedTags.changedTag ) ):

                    # If this is the first changedTag, print a full line of data...
                    if x == 0:

                        print( actions[ change.action ].ljust( 6, ' '), 
                            change.doGet.ljust( 6, ' ' ), 
                            change.type.ljust( 20, ' ' ), 
                            change.uuid,
                            change.changedTags.changedTag[ x ].name.ljust( 15, ' '),
                            change.changedTags.changedTag[ x ]._value_1
                            )

                    # otherwise print just the field/value part of the line
                    else:

                        print( 71 * ' ',
                            change.changedTags.changedTag[ x ].name.ljust( 15, ' '),
                            change.changedTags.changedTag[ x ]._value_1
                            ) 

            # otherwise just print the minimum details
            else:

                print( actions[ change.action ].ljust( 6, ' '), 
                    change.doGet.ljust( 6, ' ' ), 
                    change.type.ljust( 20, ' ' ), 
                    change.uuid
                    )

    # Update the next highest change Id
    nextStartChangeId = resp.queueInfo.nextStartChangeId    

    time.sleep( 10 )




