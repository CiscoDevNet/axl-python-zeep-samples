"""AXL addPhone sample script showing how to work-around issues with
the XBusyLampfield WSDL object, using the Zeep SOAP library.

Creates a test CSF device via <addPhone>, including direct/DN busyLampFields.

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

# To enabled SSL cert checking (recommended for production)
# place the CUCM Tomcat cert .pem file in the root of the project
# and uncomment the line below

# session.verify = 'changeme.pem'

# Add Basic Auth credentials
session.auth = HTTPBasicAuth(os.getenv("AXL_USERNAME"), os.getenv("AXL_PASSWORD"))

# Create a Zeep transport and set a reasonable timeout value
transport = Transport(session=session, timeout=10)

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

# If debug output is requested, add the MyLoggingPlugin callback
plugin = [MyLoggingPlugin()] if DEBUG else []

# Create the Zeep client with the specified settings
client = Client(WSDL_FILE, settings=settings, transport=transport, plugins=plugin)

# Create the Zeep service binding to AXL at the specified CUCM
service = client.create_service(
    "{http://www.cisco.com/AXLAPIService/}AXLAPIBinding",
    f'https://{os.getenv( "CUCM_ADDRESS" )}:8443/axl/',
)

# Create a test Line
line = {
    "pattern": "1234567890",
    "description": "Test Line",
    "usage": "Device",
    "routePartitionName": None,
}

# Execute the addLine request
try:
    resp = service.addLine(line)

except Fault as err:
    print(f"Zeep error: addLine: { err }")
    sys.exit(1)

print("\naddLine response:\n")
print(resp, "\n")

input("Press Enter to continue...")

# Create a test phone, associating the User and Line
#   Note, values with xsd.SkipValue are required by the schema
#   but not by the AXL implementation and can be skipped/left-out of the request
phone = {
    "name": "SEP123456789012",
    "product": "Cisco 7975",
    "model": "Cisco 7975",
    "class": "Phone",
    "protocol": "SIP",
    "protocolSide": "User",
    "devicePoolName": "Default",
    "locationName": "Hub_None",
    "sipProfileName": "Standard SIP Profile",
    "commonPhoneConfigName": xsd.SkipValue,
    "phoneTemplateName": xsd.SkipValue,
    "primaryPhoneName": xsd.SkipValue,
    "useTrustedRelayPoint": xsd.SkipValue,
    "builtInBridgeStatus": xsd.SkipValue,
    "packetCaptureMode": xsd.SkipValue,
    "certificateOperation": xsd.SkipValue,
    "deviceMobilityMode": xsd.SkipValue,
    "busyLampFields": {
        "busyLampField": [
            {
                "blfDest": "1000",
                "blfDirn": xsd.SkipValue,
                "routePartition": xsd.SkipValue,
                "index": 1,
            },
            {
                "blfDest": xsd.SkipValue,
                "blfDirn": "1234567890",
                "routePartition": "",
                "index": 2,
            },
        ]
    },
}

# Execute the addPhone request
try:
    resp = service.addPhone(phone)

except Fault as err:
    print(f"Zeep error: addPhone: { err }")
    sys.exit(1)

print("\naddPhone response:\n")
print(resp, "\n")

input("Press Enter to continue...")

# Execute a getPhone request to retrieve the phone we just created
try:
    resp = service.getPhone(name="SEP123456789012")

except Fault as err:
    print(f"Zeep error: getPhone: { err }")
    sys.exit(1)

print("\ngetPhone: SUCCESS!\n")
print("BLF configuration:")
print("=======================")

for busyLampField in resp["return"]["phone"]["busyLampFields"]["busyLampField"]:
    print(f"Index: {busyLampField['index']}")
    print(f"\tblfDest: {busyLampField['blfDest']}")
    print(f"\tblfDirn: {busyLampField['blfDirn']}")
    print(f"\troutePartition: {busyLampField['routePartition']}")

print()

input("Press Enter to continue...")

# Cleanup the objects we just created
try:
    resp = service.removeLine(pattern="1234567890")
except Fault as err:
    print(f"Zeep error: removeLine: { err }")
    sys.exit(1)

print("\nremoveLine response:")
print(resp, "\n")

try:
    resp = service.removePhone(name="SEP123456789012")
except Fault as err:
    print(f"Zeep error: removePhone: { err }")
    sys.exit(1)

print("\nremovePhone response:")
print(resp, "\n")
