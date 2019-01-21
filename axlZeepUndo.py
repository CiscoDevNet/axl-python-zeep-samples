"""AXL <removeLine>, <removePhone>, <removeUser> sample script, using the zeep library

Install Python 2.7 or 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

    $ python -m pip install --upgrade pip

Script Dependencies:
    lxml
    requests
    zeep

Dependency Installation:

    $ pip install zeep

This will install automatically all of zeep dependencies, including lxml, requests

Copyright (c) 2018 Cisco and/or its affiliates.
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
from zeep.plugins import HistoryPlugin
from zeep.exceptions import Fault

WSDL_URL = 'AXLAPI.wsdl'
CUCM_URL = 'https://10.10.20.1:8443/axl/'
USERNAME = 'administrator'
PASSWD = 'ciscopsdt'

#CERT = 'some.pem'

LINEDN = '1111'
PHONEID = 'SEP151515151515'
USERFNAME = 'johnq'
USERLNAME = 'public'
USERPASS = 'public'

# history shows http_headers, important if you want to re-use JSESSIONID
history = HistoryPlugin()

# This class lets you view the incoming and outgoing XML
class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

session = Session()
session.verify = False
#session.verify = CERT
session.auth = HTTPBasicAuth(USERNAME, PASSWD)

transport = Transport(session=session, timeout=10, cache=SqliteCache())

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

client = Client(WSDL_URL, settings=settings, transport=transport, plugins=[MyLoggingPlugin(),history])

service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)

line_data = {
    'pattern' : LINEDN
}

try:
	line_resp = service.removeLine(**line_data)
except Fault as err:
	print("Zeep error: {0}".format(err))
else:
	l = line_resp
	print("\nremoveLine response:\n")
	print(l,"\n")
	print(history.last_sent)
	print(history.last_received)

phone_data = {
    'name': PHONEID
}

try:
	phone_resp = service.removePhone(**phone_data)
except Fault as err:
	print("Zeep error: {0}".format(err))
else:
	p = phone_resp
	print("\nremovePhone response:\n")
	print(p,"\n")
	print(history.last_sent)
	print(history.last_received)

user_data = {
    'userid': USERFNAME
}

try:
	user_resp = service.removeUser(**user_data)
except Fault as err:
	print("Zeep error: {0}".format(err))
else:
	u = user_resp
	print("\nremoveUser response:\n")
	print(u,"\n")
	print(history.last_sent)
	print(history.last_received)

