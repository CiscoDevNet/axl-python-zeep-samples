# axl-python-zeep-sample

## Overview

This basic sample demonstrates how to use the Python Zeep SOAP library to provision a CUCM user, DN and phone via the AXL API

https://developer.cisco.com/site/axl/

The concepts and techniques shown can be extended to enable automated management of virtually any configuration or setting in the CUCM admin UI.

## Getting started

* Install Python 2.7 or 3.7
  On Windows, choose the option to add to PATH environment variable

* If this is a fresh installation, update pip (you may need to use `pip3` on Linux or Mac)

  ```
  $ python -m pip install --upgrade pip
  ```
  
* Dependency Installation:

  ```
  $ pip install zeep
  ```
  
* Edit axlZeep.py to specify your CUCM location and AXL user credentials

* Add the AXL WSDL files for your CUCM version

    1. From the CUCM Administration UI, download the 'Cisco AXL Tookit' from **Applications** / **Plugins**

    1. Unzip the kit, and navigate to the `schema/current` folder

    1. Copy the three WSDL files to the root directory of this project: `AXLAPI.wsdl`, `AXLEnums.xsd`, `AXLSoap.xsd`

## Hints

* You can get a 'dump' of the AXL WSDL to see how Zeep interprets it by copying the AXL WSDL files to the project root (see above) and running (Mac/Linux):

    ```
    python3 -mzeep AXLAPI.wsdl > wsdl.txt
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

    ```json
    { 
        members: {
            member: [
                {
                    "subElement1": None,
                    "subElement2": None
                },
                                {
                    "subElement1": None,
                    "subElement2": None
                }
            ]
        }
    }
    ```

## Available samples

* `axlZeep.py` - Demonstrates adding a user, line, and phone (`<addLine>`, `<addPhone>`, `<addUser>`, `<updatePhone>`, `<getUser>`)`

* `axl_updateDevicePool` - Demonstrates updating an existing Device Pool to modify the Local Route Group settings (`<updateDevicePool>`)

* `axl_add_partition_css.py` - Adds two partitions, then adds a CSS containing the two new partitions (`<addRoutePartition>`, `<addCss>`)

* `axl_FAC.py` - Adds a new FAC, updates it, then deletes it (`<addFacInfo>`, `<updateFacInfo>`, `<removeFacInfo>`)

* `axl_add_sip_trunk.py` - Adds a new SIP trunk with destination address, then deletes it (`<addSipTrunk`, `<removeSipTrunk>`)

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/axl-python-zeep-sample)
