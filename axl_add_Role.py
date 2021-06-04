"""Creates a new user role via <executeSqlUpdate>, then creates a custom user 
group with the new role.  Finally the role/group are removed.

Copyright (c) 2021 Cisco and/or its affiliates.
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
import sys
import urllib3

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.exceptions import Fault

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
                                f'https://{os.getenv("CUCM_ADDRESS")}:8443/axl/' )

# SQL to create a new role in the functionrole table
sql = f'''INSERT INTO functionrole (pkid,description,name)
            VALUES ( newid(),"testRole description","testRole")'''

# Execute the executeSQLUpdate request
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate/insert into functionrole: { err }' )
    sys.exit( 1 )

# SQL to retrieve the pkid of the newly created role
sql = 'SELECT pkid FROM functionrole WHERE name = "testRole"'

# Execute the executeSQLQuery request
try:
    resp = service.executeSQLQuery( sql )
except Fault as err:
    print( f'Zeep error: executeSQLQuery from functionrole: { err }' )
    sys.exit( 1 )

rolePkid = resp['return'].row[0][0].text

print( f'\nNew role pkid: { rolePkid }' )

input( '\nPress Enter to continue...' )

# SQL to create an entry in functionroleresourcemap, indicating which
# low-level system permission(s) are associated with the role
#   resource: from table typeresource (96 is 'AXL Database API')
#   permission: Usage varies by the type of resource, in general for allow/disallow items
#      this will be '1', for read and/or update items it will be 1 (read only), 2 (update only), 3 (both)
#      For AXL Database API, the permission is 1 for 'Allow to use API'

sql = f'''INSERT INTO functionroleresourcemap (pkid,fkfunctionrole,tkresource,permission)
            VALUES (newid(),"{ rolePkid }",96,1)'''

# Execute the executeSQLUpdate request
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate from functionroleresourcemap: { err }' )
    sys.exit( 1 )

# SQL to retrieve the pkid of the newly created roleresource mapping
sql = f'''SELECT pkid FROM functionroleresourcemap WHERE 
            fkfunctionrole = "{ rolePkid }" AND
            tkresource = 96 AND
            permission = 1'''

# Execute the executeSQLQuery request
try:
    resp = service.executeSQLQuery( sql )
except Fault as err:
    print( f'Zeep error: executeSQLQuery from functionroleresourcemap: { err }' )
    sys.exit( 1 )

mappingPkid = resp['return'].row[0][0].text

print( f'\nNew functionroleresourcemap pkid: { mappingPkid }' )

input( '\nPress Enter to continue...' )

# Cleanup the objects we just created
sql = f'DELETE FROM functionroleresourcemap WHERE pkid = "{ mappingPkid }"'
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate delete from functionroleresourcemap: {err}' )
    sys.exit( 1 )

print( '\nRemove functionroleresourcemap entry response: SUCCESS' )

sql = f'DELETE FROM functionrole WHERE pkid = "{ rolePkid }"'
try:
    resp = service.executeSQLUpdate( sql )
except Fault as err:
    print( f'Zeep error: executeSQLUpdate delete from functionrole: {err}' )
    sys.exit( 1 )

print( '\nRemove functionrole entry response: SUCCESS' )








