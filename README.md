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

## Available samples

* `axlZeep.py` - Demonstrates adding a user, line, and phone (`<addLine>, <addPhone>, <addUser>, <updatePhone>, <getUser>)`

* `axl_updateDevicePool` - Demonstrates updating an existing Device Pool to modify the Local Route Group settings (`<updateDevicePool>`)

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/CiscoDevNet/axl-python-zeep-sample)
