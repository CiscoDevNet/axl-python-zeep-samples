"""AXL <addLine>, <addPhone>, <addUser>, <updatePhone>, <getUser> sample script, using the zeep library

Install Python 2.7 or 3.7
On Windows, choose the option to add to PATH environment variable

If this is a fresh installation, update pip

    $ python -m pip install --upgrade pip

Script Dependencies:
    lxml
    requests
    zeep

Depencency Installation:

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

from zeep import Client, Settings, Plugin
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.plugins import HistoryPlugin

WSDL_URL = 'AXLAPI.wsdl'

# These are sample values for DevNet sandbox
# replace them with values for your own CUCM, if needed

CUCM_URL = 'https://10.10.20.1:8443/axl/'
USERNAME = 'administrator'
PASSWD = 'ciscopsdt'

# If you have a pem file certificate for CUCM, uncomment and define it here

#CERT = 'some.pem'

# These values should work with a DevNet sandbox
# You may need to change them if you are working with your own CUCM server

LINEDN = '1111'
PHONEID = 'SEP151515151515'
USERFNAME = 'johnq'
USERLNAME = 'public'
USERPASS = 'public'

# history shows http_headers
history = HistoryPlugin()

# This class lets you view the incoming and outgoing http headers and/or XML
class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
# uncomment the next line to see incoming XML
#        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
# uncomment the next line to see outgoing XML
#        print(etree.tostring(envelope, pretty_print=True))
        return envelope, http_headers

# This is where the meat of the application starts
# The first step is to create a SOAP client session

session = Session()

# We avoid certificate verification by default, but you can uncomment and set
# your certificate here, and comment out the False setting

#session.verify = CERT
session.verify = False
session.auth = HTTPBasicAuth(USERNAME, PASSWD)

transport = Transport(session=session, timeout=10, cache=SqliteCache())

# strict=False is not always necessary, but it allows zeep to parse imperfect XML
settings = Settings(strict=False, xml_huge_tree=True)

client = Client(WSDL_URL, settings=settings, transport=transport, plugins=[MyLoggingPlugin(),history])

service = client.create_service("{http://www.cisco.com/AXLAPIService/}AXLAPIBinding", CUCM_URL)

line_data = {
    'line': {
        'pattern': LINEDN,
        'description': 'Test Line',
        'usage': 'Device',
        'routePartitionName': None
    }
}

line_resp = service.addLine(**line_data)

l = line_resp
print("\naddLine response:\n")
print(l,"\n")
# uncomment these lines to see headers sent and received
#print(history.last_sent)
#print(history.last_received)

phone_data = {
    'phone': {
        'name': PHONEID,
        'description': PHONEID,
        'product': 'Cisco 8821',
        'class': 'Phone',
        'protocol': 'SIP',
        'devicePoolName': {
            '_value_1': 'Default'
        },
        'commonPhoneConfigName': {
            '_value_1': 'Standard Common Phone Profile'
        },
        'networkLocation': 'Use System Default',
        'locationName': {
            '_value_1': 'Hub_None'
        },
        'mlppIndicationStatus': 'Default',
        'preemption': 'Default',
        'useTrustedRelayPoint': 'Default',
        'retryVideoCallAsAudio': 'true',
        'securityProfileName': {
            '_value_1': 'Cisco 8821 - Standard SIP Non-Secure Profile'
        },
        'sipProfileName': {
            '_value_1': 'Standard SIP Profile'
        },
        'lines': {
            'line': [
                {
                    'index': 1,
                    'dirn': {
                        'pattern': LINEDN,
                        'routePartitionName': None
                    },
                    'ringSetting': 'Use System Default',
                    'consecutiveRingSetting': 'Use System Default',
                    'ringSettingIdlePickupAlert': 'Use System Default',
                    'ringSettingActivePickupAlert': 'Use System Default',
                    'missedCallLogging': 'true',
                    'recordingMediaSource': 'Gateway Preferred',
                }
            ],
        },
        'phoneTemplateName': {
            '_value_1': 'Standard 8821 SIP'
        },
        'ringSettingIdleBlfAudibleAlert': 'Default',
        'ringSettingBusyBlfAudibleAlert': 'Default',
        'enableExtensionMobility': 'false',
        'singleButtonBarge': 'Off',
        'joinAcrossLines': 'Off',
        'builtInBridgeStatus': 'Default',
        'callInfoPrivacyStatus': 'Default',
        'hlogStatus': 'On',
        'ignorePresentationIndicators': 'false',
        'allowCtiControlFlag': 'true',
        'presenceGroupName': {
            '_value_1': 'Standard Presence group'
        },
        'unattendedPort': 'false',
        'requireDtmfReception': 'false',
        'rfc2833Disabled': 'false',
        'certificateOperation': 'No Pending Operation',
        'dndOption': 'Use Common Phone Profile Setting',
        'dndStatus': 'false',
        'isActive': 'true',
        'isDualMode': 'false',
        'phoneSuite': 'Default',
        'phoneServiceDisplay': 'Default',
        'isProtected': 'false',
        'mtpRequired': 'false',
        'mtpPreferedCodec': '711ulaw',
        'outboundCallRollover': 'No Rollover',
        'hotlineDevice': 'false',
        'alwaysUsePrimeLine': 'Default',
        'alwaysUsePrimeLineForVoiceMessage': 'Default',
        'deviceTrustMode': 'Not Trusted',
        'earlyOfferSupportForVoiceCall': 'false'
    }
}

phone_resp = service.addPhone(**phone_data)

p = phone_resp
print("\naddPhone response:\n")
print(p,"\n")
#print(history.last_sent)
#print(history.last_received)

user_data = {
    'user': {
        'firstName': USERFNAME,
        'lastName': USERLNAME,
        'userid': USERFNAME,
        'password': USERPASS,
        'pin': '5555',
        'userLocale': 'English United States',
        'associatedDevices': {
            'device': [
                PHONEID
            ]
        },
        'primaryExtension': {
            'pattern': LINEDN,
            'routePartitionName': None
        },
        'associatedGroups': {
            'userGroup': [
                {
                    'name': 'Standard CCM End Users',
                    'userRoles': {
                        'userRole': [
                            'Standard CCM End Users',
                            'Standard CCMUSER Administration'
                        ]
                    }
                },
                {
                    'name': 'Standard CTI Enabled',
                    'userRoles': {
                        'userRole': [
                            'Standard CTI Enabled'
                        ]
                    }
                },
                {
                    'name': 'Third Party Application Users'
                },
                {
                    'name': 'Application Client Users'
                }
            ]
        },
        'enableCti': 'true',
        'presenceGroupName': {
            '_value_1': 'Standard Presence group'
        },
        'enableMobility': 'true',
        'enableMobileVoiceAccess': 'true',
        'maxDeskPickupWaitTime': 10000,
        'remoteDestinationLimit': 4,
        'passwordCredentials': {
            'pwdCredPolicyName': {
                '_value_1': 'Default Credential Policy'
            }
        },
        'enableEmcc': 'false',
        'homeCluster': 'true',
        'imAndPresenceEnable': 'true',
        'calendarPresence': 'false'
    }
}

user_resp = service.addUser(**user_data)

u = user_resp
print("\naddUser response:\n")
print(u,"\n")
#print(history.last_sent)
#print(history.last_received)

phone_data = {
    'name': PHONEID,
    'ownerUserName': USERFNAME,
    'lines': {
        'line': [
            {
                'index': 1,
                'dirn': {
                    'pattern': LINEDN,
                    'routePartitionName': None
                },
                'associatedEndusers': {
                    'enduser': [
                        {
                            'userId': 'johnq'
                        }
                    ]
                }
            }
        ],
    }
}

phone_resp = service.updatePhone(**phone_data)

p = phone_resp
print("\nupdatePhone Response\n")
print(p,"\n")
#print(history.last_sent)
#print(history.last_received)

user_data = {
    'userid': USERFNAME
}

# You'd think you could use returnedTags, but...
# returnedTags doesn't work as expected using zeep
# zeep will return much more than you request
#user_data = {
#    'userid': 'dstaudt',
#    'returnedTags' : {
#       'firstName' : '',
#       'lastName' : ''
#    }
#}

user_resp = service.getUser(**user_data)

fname = user_resp['return']['user']['firstName']
lname = user_resp['return']['user']['lastName']
print("\ngetUser response:\n")
print(fname, lname, "\n")
#print(history.last_sent)
#print(history.last_received)
