# axl-python-zeep-samples

## Overview

These samples demonstrates how to use the Python Zeep SOAP library to read/update CUCM configurations via the AXL SOAP API.

[https://developer.cisco.com/site/axl/](https://developer.cisco.com/site/axl/)

The concepts and techniques shown can be extended to enable automated management of virtually any configuration or setting in the CUCM admin UI.

## Available samples

* `axlZeep.py` - Demonstrates adding a user, line, and phone ( `<addLine>`, `<addPhone>`, `<addUser>`, `<updatePhone>`, `<getUser>` ).

* `axl_add_updateLine.py` - Creates a line, then performs updateLine to modify the call pickup group ( `<addCallPickupGroup>`, `<addLine>`, `<updateLine>`).

* `axl_updateDevicePool` - Demonstrates creating a Device Pool and its sub-objects, then updating the Device Pool's Local Route Group Settings ( `<addDevicePool>`, `<addH323Gateway>`, `<addRouteGroup>`, `<addLocalRouteGroup>`, `<updateDevicePool>`).

* `axl_add_partition_css.py` - Adds two partitions, then adds a CSS containing the two new partitions ( `<addRoutePartition>`, `<addCss>` ).

* `axl_FAC.py` - Adds a new FAC, then updates it ( `<addFacInfo>`, `<updateFacInfo>`).

* `axl_add_sip_trunk.py` - Adds a new SIP trunk with destination address ( `<addSipTrunk`).

* `axl_executeSQLQuery.py` - Creates a Call Pickup Group and associates two test Lines, then executes a SQL query joining the numplan, pickupgrouplinemap, and pickupgroup tables to list the DNs belonging to the pickup group ( `<addCallPickupGroup>`, `<addLine>`, `<executeSQLQuery>`).

* `axl_executeSQLUpdate.py` - Creates a set of UC Services of type Video Conference Scheduling Portal, and an empty Service Profile.   Then executes a SQL update to associate the primary/secondary Services to the Profile (`<addUcService>`, `<addServiceProfile>`, `<executeSQLUpdate>`).

* `axl_addRemoteDestination.py` - Creates an EndUser, and associates a new Remote Destination Profile, then adds a Remote Destination (`<addUser>`, `<addRemoteDestinationProfile>`, `<addRemoteDestination>` ).

* `axl_addAppUser.py` - Creates a CSF Phone device, then creates an Application User and associates the new device.  Finally the Application User and Phone are removed (`<addAppUser>`).

* `axl_add_update_User.py` - Creates a CSF phone device, then creates a new End-User and associates the new device via `<updateUser>` (`<addPhone>`, `<addUser>`, `<updateUser>`).

* `axl_listChange.py` - Demonstrates usage of the AXL 'Data Change Notification' feature to continuosly monitor and display incremental changes to the CUCM configuration database (`<listChange>`).

* `axl_add_update_Device_Pool.py` - Creates a new Device Pool, then creates a new Media Resource Group List and updates the Device Pool (`<addDevicePool>`, `<addMediaResourceList>`,`<updateDevicePool>`).

* `axl_add_Route_Pattern.py` - Creates a Route List, then creates a Route Pattern using the new Route List (`<addRouteList>`, `<addRoutePattern>`).

* `axl_add_Region.py` - Creates a Region including a region relationship  (`<addRegion>`).

* `axl_add_Location.py` - Add a new Location including related Location and between Location settings  (`<addLocation>`).

* `axl_add_User_Line_Phone.py` - Creates a new Line and Phone, associates the two; then creates a new End User, and associates with the new Phone (`<addLine>`, `<addPhone>`, `<addUser>`).

* `axl_update_Service_Parameter.py` - Lists all Process Nodes with "CUCM Voice/Video" role, then for each sets the "Cisco CallManager" service parameter "CdrEnabled" to true (`<listProcessNode>`, `<updateServiceParameter>`).

* `axl_doAuthenticateUser.py` - Creates an End User with password and PIN, authenticates the user using each, then deletes the user (`<addUser>`, `<doAuthenticateUser>`).

* `axl_addGateway.py` - Creates a VG310 MGCP gateway with unit VG-2VWIC-MBRD and subunit 24FXS, then adds a new analog/POTS port/line to the subunit (`<addGateway>`, `<addGatewayEndpointAnalogAccess>`, `<addLine>`).

* `axl_executeSQLUpdate_Jabber_config.py` - demonstrates provisioning a Jabber config UC Service via <executeSQLUpdate> operations (`<executeSQLUpdate>`, `<executeSQLQuery>`).

* `axl_add_update_Line.py` - Creates a new Line with Call Forward All set to VoiceMail, then performs an updateLine request to clear the CFA setting (`<addLine>`, `<updateLine>`).

* `axl_add_Phone_vendorConfig.py` - Creates a test CSF device, including Product Specific settings in `<vendorConfig>`, then retrieves/parses the setting via (`<addPhone>`, `<getPhone>`).

* `axl_add_DateTimeGroup.py` - Creates a two Phone NTP References, then creates a new Date Time Group using the NTP References (`<addPhoneNtp>`, `<addDateTimeGroup>`).

## Getting started

* Install Python 3

    On Windows, choose the option to add to PATH environment variable

* (Optional) Create/activate a Python virtual environment named `venv`:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
* Install needed dependency packages:

    ```bash
    pip install -r requirements.txt
    ```

* Rename `.env.example` to `.env`, and edit it to specify your CUCM address and AXL user credentials.

* The AXL v12.5 WSDL files are included in this project.  If you'd like to use a different version, replace with the AXL WSDL files for your CUCM version:

    1. From the CUCM Administration UI, download the 'Cisco AXL Tookit' from **Applications** / **Plugins**

    1. Unzip the kit, and navigate to the `schema/current` folder

    1. Copy the three WSDL files to the `schema/` directory of this project: `AXLAPI.wsdl`, `AXLEnums.xsd`, `AXLSoap.xsd`

* To run a specific sample, in Visual Studio Code open the sample `.py` file you want to run, then press `F5`, or open the Debugging panel and click the green 'Launch' arrow

## Hints

* You can get a 'dump' of the AXL WSDL to see how Zeep interprets it by copying the AXL WSDL files to the project root (see above) and running (Mac/Linux):

    ```bash
    python3 -mzeep schema/AXLAPI.wsdl > wsdl.txt
    ```

    This can help with identifying the proper object structure to send to Zeep

* Elements which contain a list, such as:

    ```xml
    <members>
        <member>
            <subElement1/>
            <subElement2/>
        </member>
        <member>
            <subElement1/>
            <subElement2/>
        </member>
    </members>
    ```

    are represented a little differently than expected by Zeep.  Note that `<member>` becomes an array, not `<members>`:

    ```python
    {
        'members': {
            'member': [
                {
                    'subElement1': 'value',
                    'subElement2': 'value'
                },
                {
                    'subElement1': 'value',
                    'subElement2': 'value'
                }
            ]
        }
    }
    ```

* Zeep expects elements with attributes and values to be constructed as below:

    To generate this XML...

    ```xml
    <startChangeId queueId='foo'>bar</startChangeId>
    ```

    Define the object like this...

    ```python
    startChangeId = {
        'queueId': 'fee',
        '_value_1': 'bar'
    }
    ```
* **Requests Sessions** While creating and using a [Requests Session](https://2.python-requests.org/en/master/user/advanced/#id1) object to use with Zeep allows disabling certificate verfication during development via `session.verify = False`, you should also use a Session even if you don't need to disable cert checks. 

    This allows Zeep to use AXL cookies and HTTP persistent connections to keep CUCM resource impact low: fresh user authentication checks and Tomcat sessions are expensive, and CUCM socket connections are not unlimited...

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/axl-python-zeep-sample)
