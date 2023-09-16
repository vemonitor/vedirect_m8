# VeDirect M8

[![CircleCI](https://circleci.com/gh/mano8/vedirect_m8.svg?style=svg)](https://app.circleci.com/pipelines/github/mano8/vedirect_m8)
[![PyPI package](https://img.shields.io/pypi/v/vedirect_m8.svg)](https://pypi.org/project/vedirect_m8/)
[![Known Vulnerabilities](https://snyk.io/test/github/mano8/vedirect_m8/badge.svg)](https://snyk.io/test/github/mano8/vedirect_m8)
[![codecov](https://codecov.io/gh/mano8/vedirect_m8/branch/main/graph/badge.svg?token=KkAwHvkse6)](https://codecov.io/gh/mano8/vedirect_m8)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/c401bed6812d4f9bb77bfaee16cf0abe)](https://www.codacy.com/gh/mano8/vedirect_m8/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mano8/vedirect_m8&amp;utm_campaign=Badge_Grade)
[![Downloads](https://static.pepy.tech/badge/vedirect_m8)](https://pepy.tech/project/vedirect_m8)

## Sponsors
<p  align="center" width="100%">
  <a href="https://jb.gg/OpenSourceSupport" target="_blank" rel="noreferrer noopener" align="center"> 
    <img src="https://resources.jetbrains.com/storage/products/company/brand/logos/jb_beam.png" alt="JetBrains Logo (Main) logo." width="100" />
  </a>
  
</p>
<p  align="center" width="100%">
  <span width="50%">Thanks Jetbrains to Support this repository.</span>
</p>

## Description
This is a Python library for decoding the Victron Energy VE.Direct text protocol
used in their range of MPPT solar charge controllers and battery monitors.

This is a forked version of a package originally created by Janne Kario
[VeDirect](https://github.com/karioja/vedirect).

## Installation

To install directly from GitHub:

``$ python3 -m pip install "git+https://github.com/mano8/vedirect_m8"``

To install from PypI :

``python3 -m pip install vedirect_m8``

## Test on virtual serial port

The sim_data directory contains a set of live recordings of the serial port data
sent by the 3 devices that I own.

* SmartSolar MPPT 100/20 running firmware version 1.39
* BlueSolar MPPT 75/15 running firmware version 1.23
* BVM 702 battery monitor running firmware version 3.08

On unix systems, these recordings can be fed to the Vedirect decoder
using a pair of virtual serial ports.

First you need install socat on your machine.
On debian systems type on your terminal :

```plaintext
$ sudo apt-get install socat
```

Next install the vedirect_m8 package ``see above``.

Now, to create a pair of virtual serial ports issue the following command:

```plaintext
$ socat -d -d PTY,raw,echo=0,link=/${HOME}/vmodem0 PTY,raw,echo=0,link=/${HOME}/vmodem1
```

This will create 2 virtual serials ports connected to each other.

Anything sent to ```/${HOME}/vmodem0``` will be echoed to ```/${HOME}/vmodem1``` and vice versa.

In other terminal, run the vedirectsim script with your desired device:

```plaintext
$ python examples/vedirectsim.py --port /${HOME}/vmodem0 --device bmv700
```

Or if you need to see the inputs sent on serial port :

```plaintext
$ python examples/vedirectsim.py --port /${HOME}/vmodem0 --device bmv700 --debug
```
Device option must be ``bmv700, bluesolar_1.23, or smartsolar_1.39``.

Then, in other terminal, attach the decoder to /${HOME}/vmodem1:

```plaintext
$ python examples/vedirect_print.py --port /${HOME}/vmodem1
```

All the inputs from the selected device file, are encoded to the vmodem0 serial port,
then echoed to the vmodem1 by socat, and finally decoded by the vedirect module.

## The Vedirect Controller

This script extends from Vedirect,
and add ability to automate connection to serial port.

Useful if you don't know the serial port,
or if you disconnect VeDirect USB cables and don't reconnect on sames USB ports.

To do so, we need a serialTest extra configuration settings.

Warning, all the test must successful for validate the serial port.

### Available serialTest

Two test types, can be used to validate a serial port.

#### 1. Value Tests

This type of test evaluates whether the key value from the decoded data
is equal to the provided value.

The configuration must contain the following parameters :

* typeTest: must be equal to ```value``` here.
* key: the key of the value to tested from decoded data
* value: the value to test must be equal of the value of the key from decoded data

Must be used only on static keys values egg ```PID```, ```SER#``` or , ```FW```.

Example for the bmv702 device from sim_data directory:

```plaintext
'serialTest':{
    'PID_test': { 
        "typeTest": "value",
        "key": "PID",
        "value": "0x203" # the value to test
    },
    'FW_test': { 
        "typeTest": "value",
        "key": "FW",
        "value": "308" # the value to test
    }
}
```

In this example, we search a serial port, sending vedirect encoded data
containing at least, </br>
the keys ```PID``` and ```FW```, whose values are respectively
```0x203``` and ```308```.

#### 2. Column keys Tests

This type of test evaluates whether the all the keys provided exists
in the decoded data.

The configuration must contain the following parameters :

* typeTest: must be equal to ```value``` here.
* keys: the keys that must be present in the decoded data

Example for the bmv702 device from sim_data directory:

```plaintext
"serialTest": {
    'KeysTest': {
        "typeTest": "value",
        "keys": ["V", "I", "P", "CE", "SOC", "H18"]
    }
}
```

In this example, we search a serial port, sending vedirect encoded data
containing at least, </br>
the keys ```[ "V", "I", "P", "CE", "SOC", "H18" ]```

### Complete configuration example

Example with Complete configuration :

```python
from vedirect_m8.ve_controller import VedirectController

def print_data_callback(packet):
    print(packet)

if __name__ == '__main__':
    conf = {
        'serialPort': "/${HOME}/vmodem1",
        'timeout': 0,
        
        'serialTest':{ 
            'PID_test': { 
                "typeTest": "value",
                "key": "PID",
                "value": "0x203"
            },
            'FW_test': { 
                "typeTest": "value",
                "key": "FW",
                "value": "308"
            },
            "KeysTest": {
                "typeTest": "columns",
                "keys": [ "V", "I", "P", "CE", "SOC", "H18" ]
            }
        }
    }
    ve = VedirectController(**conf)
    ve.read_data_callback(print_data_callback)
```

In this example, we search a serial port,
sending vedirect encoded data containing at least:

* the keys ```[ "V", "I", "P", "CE", "SOC", "H18" ]```
* and the keys ```PID``` and ```FW```,
  whose values are respectively ```0x203``` and ```308```.

When the script is initialized, it first tries to connect to the
```/${HOME}/vmodem1``` serial port. 

If the connection fails, it waits for an available serial port
that matches all the tests above.

Then, when a valid serial port is found, it will start
to decode VeDirect data from that serial port normally.

Later, if you disconnect the serial USB cable
and reconnect it to another USB port, the serial port
will change and the connection will fail.

This will restart the same process, it is waiting for an available serial port
that matches all the tests above. Then, when a valid serial port is found,
it resumes decoding VeDirect data from that serial port normally.
