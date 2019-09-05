# axl-python-zeep-samples

## Overview

This basic sample demonstrates how to use the Python Zeep SOAP library to provision a CUCM user, DN and phone via the AXL API

[https://developer.cisco.com/site/axl/](https://developer.cisco.com/site/axl/)

The concepts and techniques shown can be extended to enable automated management of virtually any configuration or setting in the CUCM admin UI.

## Available samples

* `axlZeep.py` - Demonstrates adding a user, line, and phone ( `<addLine>`, `<addPhone>`, `<addUser>`, `<updatePhone>`, `<getUser>` )

* `axl_add_updateLine.py` - Creates a line, then performs updateLine to modify the call pickup group ( `<addCallPickupGroup>`, `<addLine>`, `<updateLine>`, `<removeLine>`, `<removeCallPickupGroup>`)

* `axl_updateDevicePool` - Demonstrates creating a Device Pool and its sub-objects, then updating the Device Pool's Local Route Group Settings ( `<addDevicePool>`, `<addH323Gateway>`, `<addRouteGroup>`, `<addLocalRouteGroup>`, `<updateDevicePool>`, `<removeH323Gateway>`, `<removeDevicePool>`, `<removeLocalRouteGroup>`, `<removeRouteGroup>` )

* `axl_add_partition_css.py` - Adds two partitions, then adds a CSS containing the two new partitions ( `<addRoutePartition>`, `<addCss>` )

* `axl_FAC.py` - Adds a new FAC, then updates it ( `<addFacInfo>`, `<updateFacInfo>`, `<removeFacInfo>` )

* `axl_add_sip_trunk.py` - Adds a new SIP trunk with destination address ( `<addSipTrunk`, `<removeSipTrunk>` )

* `axl_executeSQLQuery.py` - Creates a Call Pickup Group and associates two test Lines, then executes a SQL query joining the numplan, pickupgrouplinemap, and pickupgroup tables to list the DNs belonging to the pickup group ( `<addCallPickupGroup>`, `<addLine>`, `<executeSQLQuery>`, `<removeCallPickupGroup>`, `<removeLine>` )

* `axl_executeSQLUpdate.py` - Creates a set of UC Services of type Video Conference Scheduling Portal, and an empty Service Profile.   Then executes a SQL update to associate the primary/secondary Services to the Profile (`<addUcService>`, `<addServiceProfile>`, `<executeSQLUpdate>`, `<removeServiceProfile>`, `<removeUcService>`)

* `axl_addRemoteDestination.py` - Creates an EndUser, and associates a new Remote Destination Profile, then adds a Remote Destination (`<addUser>`, `<addRemoteDestinationProfile>`, `<addRemoteDestination>` )

* `axl_addAppUser.py` - Creates a CSF Phone device, then creates an Application User and associates the new device.  Finally the Application User and Phone are removed.

## Getting started

* Install Python 3.7
  On Windows, choose the option to add to PATH environment variable

* The project was built/tested using [Visual Studio Code](https://code.visualstudio.com/)

* If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

    ```bash
    python -m pip install --upgrade pip
    ```
  
* Dependency Installation:

    ```bash
    pip install zeep
    ```
  
* Edit `creds.py` to specify your CUCM address and AXL user credentials

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

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/axl-python-zeep-sample)
