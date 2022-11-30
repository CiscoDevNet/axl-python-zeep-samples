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

* `axl_add_Role.py` - Creates a new user role via <executeSqlUpdate>, then creates a custom user group with the new role (`<executeSQLUpdate>`, `<executeSQLQuery>`).

* `axl_list_Sip_Trunk.py` - Creates two SIP Trunks, then retrieves SIP Trunk names/details and prints a simple report (`<addSipTrunk>`, `<listSipTrunk>`).

* `axl_listRegistrationDynamic.py` - Retrieves real-time registration info for devices and prints a simple report (`<listRegistrationDynamic>`).

## Getting started

* Install Python 3

    On Windows, choose the option to add to PATH environment variable

* If installing on Linux, you may need to install dependencies for `python3-lxml`, see [Installing lxml](https://lxml.de/3.3/installation.html)

  E.g. for Debian/Ubuntu:

  ```bash
  sudo apt build-dep python3-lxml
  ```    

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

* The AXL v14 WSDL files are included in this project.  If you'd like to use a different version, replace with the AXL WSDL files for your CUCM version:

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
        'queueId': 'foo',
        '_value_1': 'bar'
    }
    ```
* **xsd:SkipValue** When building the XML to send to CUCM, Zeep may include empty elements that are part of the schema but that you didn't explicity specify.  This may result in CUCM interpreting the empty element as indication to set the value to empty/nil/null.  To force Zeep to skip including an element, set its value to `xsd:SkipValue`:

   ```python
   updatePhoneObj = {
    "description": "New Description",
    "lines": xsd:SkipValue
   }
   ```

   Be sure to import the `xsd` module: `from zeep import xsd`

* **Requests Sessions** Creating and using a [requests Session](https://docs.python-requests.org/en/latest/user/advanced/) object [to use with Zeep](https://docs.python-zeep.org/en/master/api.html) allows setting global request parameters like `auth`/`verify`/`headers`.

    In addition, Session retains CUC API `JSESSION` cookies to bypass expensive backend authentication checks per-request, and HTTP persistent connections to keep network latency and networking CPU usage lower.
    
[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/axl-python-zeep-sample)
