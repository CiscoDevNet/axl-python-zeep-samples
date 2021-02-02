"""AXL <addLine>, <addPhone>, <addUser>, <updatePhone>, <getUser> sample script, using the zeep library

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
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
import sys
import urllib3

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

LINEDN = '1111'
PHONEID = 'SEP151515151515'
USERFNAME = 'johnq'
USERLNAME = 'public'
USERPASS = 'public'


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

line_data = {
    'line': {
        'pattern': LINEDN,
        'description': 'Test Line',
        'usage': 'Device',
        'routePartitionName': None
    }
}

# the ** before line_data tells the Python function to expect
# an unspecified number of keyword/value pairs

try:
	line_resp = service.addLine(**line_data)
except Fault as err:
	print("\nZeep error: {0}".format(err))
else:
	print("\naddLine response:\n")
	print(line_resp,"\n")

input( 'Press Enter to continue...' )

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

try:
  phone_resp = service.addPhone(**phone_data)
except Fault as err:
	print("\nZeep error: {0}".format(err))
else:
	print("\naddPhone response:\n")
	print(phone_resp,"\n")

input( 'Press Enter to continue...' )

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

try:
	user_resp = service.addUser(**user_data)
except Fault as err:
	print("\nZeep error: {0}".format(err))
else:
	print("\naddUser response:\n")
	print(user_resp,"\n")

input( 'Press Enter to continue...' )

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

try:
	phone_resp = service.updatePhone(**phone_data)
except Fault as err:
	print("\nZeep error: {0}".format(err))
else:
	print("\nupdatePhone response:\n")
	print(phone_resp,"\n")

input( 'Press Enter to continue...' )

user_data = {
    'userid': USERFNAME
}

# You'd think you could use returnedTags, but...
# returnedTags doesn't work as expected using zeep
# zeep will return much more than you request
#user_data = {
#    'userid': 'johnq',
#    'returnedTags' : {
#       'firstName' : '',
#       'lastName' : ''
#    }
#}

# Print the full user_resp first, which enables you to see why we access
# the values as ['return']['user']['firstname'], etc.

try:
	user_resp = service.getUser(**user_data)
except Fault as err:
	print("\nZeep error: {0}".format(err))
else:
	print("\ngetUser response:\n")
	print(user_resp,"\n\n")
	fname = user_resp['return']['user']['firstName']
	lname = user_resp['return']['user']['lastName']
	print( 'Parsed user info: {0} {1}'.format( fname, lname ) )

