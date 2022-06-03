# VeDirect M8
[![CircleCI](https://circleci.com/gh/mano8/vedirect_m8.svg?style=svg)](https://app.circleci.com/pipelines/github/mano8/vedirect_m8)
[![PyPI package](https://img.shields.io/pypi/v/vedirect_m8.svg)](https://pypi.org/project/vedirect_m8/)
   
This is a Python library for decoding the Victron Energy VE.Direct text protocol used in their range of MPPT solar charge controllers and battery monitors.

This is a forked version of a package originally created by Janne Kario (https://github.com/karioja/vedirect).

## Installation
To install directly from GitHub:

``$ python3 -m pip install "git+https://github.com/mano8/vedirect_m8"``

To install from PypI :

``python3 -m pip install vedirect_m8``

## Test on virtual serial port
The sim_data directory contains a set of live recordings of the serial port data sent by the 3 devices that I own.

* SmartSolar MPPT 100/20 running firmware version 1.39
* BlueSolar MPPT 75/15 running firmware version 1.23
* BVM 702 battery monitor running firmware version 3.08

These recordings can be fed to the Vedirect decoder using a pair of virtual serial ports.

To create a pair of virtual serial ports issue the following command:
```
$ socat -d -d PTY,raw,echo=0,link=/tmp/vmodem0 PTY,raw,echo=0,link=/tmp/vmodem1
```
This will create 2 virtual serials ports connected to each other.

Anything sent to /tmp/vmodem0 will be echoed to /tmp/vmodem1 and vice versa.

In other terminal, run the vedirectsim script with your desired device:

```
python examples/vedirectsim.py --port /tmp/vmodem0 --device bmv700
```
Device option must be ``bmv700``, ``bluesolar_1.23`` or ``smartsolar_1.39``.

Then, in other terminal, attach the decoder to /tmp/vmodem1:
```
python examples/vedirect_print.py --port /tmp/vmodem1
```
## The Vedirect Controller

This script extends from Vedirect, and add ability to automate connection to serial port.

Useful if you don't know the serial port, or if you disconnect VeDirect USB cables and don't reconnect on sames USB ports.

To do so, we need a serialTest extra configuration settings.

Warning, all the test must successful for validate the serial port.

The script run as fallow :
- If no serialPort is specified, or if the serial connection shuts down.
- The script will wait for new connection in a while loop and every 2 seconds:
    - Scan all available serial ports (only scan on /dev and /tmp)
    - For any port available* open a new serial connection
    - Run the vedirect decoder to read data from it
    - And execute the serialTests on the data
    - If the serialTests fails, restart the same process.
    - Else If all the tests are successful, break this loop and stay connected
    - Finally, continue where connection shuts down.

(*): the available ports must be validated depending on your running system :
- For Unix systems : ```r'^((?:/dev/|/tmp/)((?:(?:tty(?:USB|ACM))|(?:vmodem))(?:\d{1,5})))$'```
- For Windows systems : ```r'^(COM\d{1,3})$'```

### Available serialTest :

Two test types, can be used to validate a serial port.
#### 1. Value Tests :

This type of test evaluates whether the key value from the decoded data is equal to the provided value.

The configuration must contain the following parameters :
- typeTest: must be equal to ```value``` here.
- key: the key of the value to tested from decoded data
- value: the value to test must be equal of the value of the key from decoded data

Must be used only on static keys values egg ```PID```, ```SER#``` or , ```FW```.

Example for the bmv702 device from sim_data directory:
```
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
In this example, we search a serial port, sending vedirect encoded data containing at least, </br> the keys ```PID``` and ```FW```, whose values are respectively ```0x203``` and ```308```.

#### 2. Column keys Tests :
This type of test evaluates whether the all the keys provided exists in the decoded data.

The configuration must contain the following parameters :
- typeTest: must be equal to ```value``` here.
- keys: the keys that must be present in the decoded data

Example for the bmv702 device from sim_data directory:
```
'serialTest':{
    'KeysTest': { 
        "typeTest": "value",
        "keys": [ "V", "I", "P", "CE", "SOC", "H18" ]
    }
}
```
In this example, we search a serial port, sending vedirect encoded data containing at least, </br> the keys ```[ "V", "I", "P", "CE", "SOC", "H18" ]```

### Complete configuration example :
Here you can see a complete configuration example :
```
conf = {
    'serialPort': "/tmp/vmodem1",
    'timeout': 60,
    
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
```
In this example, we search a serial port, sending vedirect encoded data containing at least:
- the keys ```[ "V", "I", "P", "CE", "SOC", "H18" ]```
- and the keys ```PID``` and ```FW```, whose values are respectively ```0x203``` and ```308```.

When the script is initialized, it first tries to connect to the ```/tmp/vmodem1``` serial port. 

If the connection fails, it waits for an available serial port that matches all the tests above.

Then, when a valid serial port is found, it will start to decode VeDirect data from that serial port normally.

Later, if you disconnect the serial USB cable and reconnect it to another USB port, the serial port will change and the connection will fail. 

This will restart the same process, it is waiting for an available serial port that matches all the tests above. Then, when a valid serial port is found, it resumes decoding VeDirect data from that serial port normally.
