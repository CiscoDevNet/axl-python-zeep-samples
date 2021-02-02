"""AXL <executeSQLUpdate>, <executeSQLQuery> sample script, using the Zeep SOAP library

As of CUCM 12.5, <addUcService> and <updateUcService> do not support 
defining new services of type 'Jabber', for Jabber configs.  This sample
demonstrates provisioning a Jabber config UC Service via <executeSQLUpdate>
operations.

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
import textwrap
import urllib

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

# Create an object containing the raw SQL update to execute
# newid() is a built-in stored procedure for generating a new UUID primary key
# tkucproduct=42 is 'Jabber'
# tkreset=2 is 'Restart' (ignored as resettoggle=f)
sql = '''INSERT INTO ucservice ( pkid, name, tkucproduct, tkreset, resettoggle ) VALUES ( newid(), "testJabberConfig", 42, 2, 'f' )'''

# Execute the executeSQLUpdate request
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate/insert into ucservice: { err }' )
    sys.exit( 1 )

print( '\nexecuteSQLUpdate/insert into ucservice: SUCCESS' )
print( f'Rows updated: { resp[ "return" ][ "rowsUpdated" ] }' )

input( '\nPress Enter to continue...\n' )

# Retrieve the pkid of the new ucservice using executeSqlQuery
sql = 'SELECT pkid from ucservice where name="testJabberConfig"'

try:
    resp = service.executeSQLQuery( sql )
except Fault as err:
    print( f'Zeep error: executeSqlQuery/select from ucservice: { err }' )
    sys.exit( 1 )

# Parse the pkid
ucServiceId = resp[ 'return' ][ 'row' ][ 0 ][ 0 ].text

print( '\nexecuteSqlQuery/select from ucservice response: SUCCESS' )
print( f'UC Service pkid: { ucServiceId }' )

input( '\nPress Enter to continue...\n' )

# CUCM admin appears to URL encode values in the XML
value = urllib.parse.quote_plus( 'dstaudt@ds-cup1251.cisco.com' )

# Define the XML for the Jabber config file
# textwrap.dedent cleans up common leading whitespace from indented multi-line literals
xml = textwrap.dedent( f'''\
    <Options>
        <AdminConfiguredBot>{ value }</AdminConfiguredBot>
    </Options>''')

# Create SQL to add an entry into the ucservicexml table
# newid() is a built-in stored procedure for generating a new UUID primary key
sql = f'''INSERT INTO ucservicexml (pkid,fkucservice,xml)
            VALUES ( newid(),"{ ucServiceId }","{ xml }")'''

# Execute the executeSQLQuery request
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate/insert into ucservicexml: { err }' )
    sys.exit( 1 )

print( '\nexecuteSQLUpdate/insert into ucservicexml response:  SUCCESS' )
print( f'Rows updated: { resp[ "return" ][ "rowsUpdated" ] }' )

input( '\nPress Enter to continue...\n' )

# Cleanup the objects we just created
# Note the database automatically removes records from ucservicexml when the 
#   related UC Service is removed
try:
    resp = service.removeUcService( name = 'testJabberConfig' )
except Fault as err:
    print( f'Zeep error: removeUcService: { err }' )
else:
    print( '\nremoveUcService response: SUCCESS' )







