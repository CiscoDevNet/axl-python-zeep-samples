"""AXL <doChangeDNDStatus> sample script, using the Zeep SOAP library

Creates an End User with password and PIN, then enables Do Not Disturb for
the user.

Copyright (c) 2023 Cisco and/or its affiliates.
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
DEBUG = True

# The WSDL is a local file in the working directory, see README
WSDL_FILE = "schema/AXLAPI.wsdl"

# This class lets you view the incoming and outgoing http headers and XML


class MyLoggingPlugin(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        # Format the request body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding="unicode")

        print(f"\nRequest\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}")

    def ingress(self, envelope, http_headers, operation):
        # Format the response body as pretty printed XML
        xml = etree.tostring(envelope, pretty_print=True, encoding="unicode")

        print(f"\nResponse\n-------\nHeaders:\n{http_headers}\n\nBody:\n{xml}")


# The first step is to create a SOAP client session
session = Session()

# We avoid certificate verification by default
# And disable insecure request warnings to keep the output clear
session.verify = False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# To enable SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the two lines below

# CERT = 'changeme.pem'
# session.verify = CERT

session.auth = HTTPBasicAuth(os.getenv("AXL_USERNAME"), os.getenv("AXL_PASSWORD"))

transport = Transport(session=session, timeout=10)

# strict=False is not always necessary, but it allows Zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [MyLoggingPlugin()] if DEBUG else []

# Create the Zeep client with the specified settings
client = Client(WSDL_FILE, settings=settings, transport=transport, plugins=plugin)

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service(
    "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
    f'https://{os.getenv("CUCM_ADDRESS")}:8443/axl/',
)

# Create an End User
end_user = {
    "userid": "testEndUser",
    "lastName": "testEndUser",
    "password": "Cisco1234!",
    "pin": "09823490",
    "presenceGroupName": "Standard Presence Group",
}

# Execute the addUser request
try:
    resp = service.addUser(end_user)
except Exception as err:
    print(f"\nZeep error: addUser: { err }")
    sys.exit(1)

print("\naddUser response:\n")
print(resp, "\n")

input("Press Enter to continue...")

# Execute doAuthenticateUser using password
try:
    resp = service.doChangeDNDStatus(userID="testEndUser", dndStatus=True)
except Exception as err:
    print(f"\nZeep error: doChangeDNDStatus: { err }")
    sys.exit(1)

print("\ndoChangeDNDStatus response: SUCCESS\n")
print(resp, "\n")

input("Press Enter to continue...")

# Cleanup the objects we just created
try:
    resp = service.removeUser(userid="testEndUser")
except Fault as err:
    print(f"Zeep error: removeUser: { err }")
    sys.exit(1)

print("\nremoveUser response:")
print(resp, "\n")
