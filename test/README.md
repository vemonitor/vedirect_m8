# Vedirect pytest directory

Some tests will need a valid serial connection to be executed :
- ``/tmp/vmodem1`` port on unix systems
- ``COM1`` port on windows systems

## Tests on unix systems :

### Install socat :

On Ubuntu/debian systems run the command on the terminal:

``$ sudo apt-get install socat``

You can visit this [page](https://packages.debian.org/bullseye/socat) to see dependencies, on debian systems.

To create a pair of virtual serial ports issue the following command:

```
$ socat -d -d PTY,raw,echo=0,link=/tmp/vmodem0 PTY,raw,echo=0,link=/tmp/vmodem1
```

Tests will be configured to read data on serial port ``/tmp/vmodem1``.

Now in other terminal, go to the current directory where you have cloned this repository, egg :

``$ cd ~/my_repos/vedirect/vedirect``

If you use a python virtual environment egg anaconda, you need to activate him :

``$ conda activate env_name``

Replace env_name by your environment name.

Then you may execute vedirectsim.py python script on port ``/tmp/vmodem0``

``$ python vedirectsim.py --port /tmp/vmodem0``

Now encoded data will be sent from ``/tmp/vmodem0`` to ``/tmp/vmodem1``.

On other terminal, go to the current directory where you have cloned this repository, egg :

``$ cd ~/my_repos/vedirect``

Activate your virtual environment if needed, and run pytest :

``$ pytest -s``

This command will run all the unittests on this repository.

Finally, you need to exit or close the terminals to stop virtual serial ports and vedirectsim python script.

## Tests on other systems :

Sorry but I only use linux ubuntu/debian systems for that purpose.

For Windows systems you can visit [this page](https://freevirtualserialports.com/),

or search any other tool using your favorite search engine.

The unittests will be configured to read on serial port ``COM1`` for Windows systems.