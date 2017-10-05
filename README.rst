juramote
========

Remote control for Jura_ coffee maker. Currently supported:

- Xs90 (EF516M V01.25)

.. _Jura: https://www.jura.com/

Usage
-----

This software depends on Python. Both 2.7 and 3 should work. It also requires
the following packages to be installed. They are available from pypi_:

- pyserial
- Flask
- wtforms

.. _pypi: https://pypi.python.org/

The standard setuptools-based install is supported and thus as easy as typing::

    git clone https://github.com/PromyLOPh/juramote.git
    cd juramote
    pip install .

However using a virtual environment is highly recommended.

Then use ``juramotecli`` for a command line interface or set up nginx/uwsgi for
remote HTTP access. See directory contrib/ for example configs.

Protocol
--------

On the back of the machine a debug connector (female, 9 pin dsub) can be used
to access various functions. It uses the UART protocol with the following
pinout::

    5       1
     -------
     \     /
      -----
     9     6

1
    TX (output)
2
    GND
3
    RX (input)
4
    VCC (5V)

The synchronous text protocol uses a strange “transfer encoding” and stretches
one byte to four, see juramote/com.py. It provides the following (known)
commands. Integer, arguments or response, are usually hex-encoded (uppercase).

CB: → cb:00
    Unknown.
CM: → cm:300E8006006000000000000000000
    Status information. Some values are equivalent to those returned by HZ_:

    .. code:: python

       cm[0] = hz[6]
       cm[1:5] = hz[2]

CS: → cs:03EC0562300E800000000000000600601C1
    Sensor(?) status information. Some values are equivalent to
    those returned by HZ_:

    .. code:: python

        cs[0:4] = hz[4]
        cs[4:8] = hz[5]
        cs[9:13] = hz[2]
        cs[31:35] = hz[3]

    19:22
        Nonzero when brewing, 0x1FF for the first step, 0x3FF for the second
    22:25
        Nonzero (usually 0x3FF) when grinding
DA:<message>
    Print permanent message on display. Argument is latin1 encoded string.
DR:
    Reset display.
DT:<message>
    Change default message (“Bitte wählen”).
FA:<id>
    Press button id. Argument is 8 bit button id.
FN:<id>
    Control component (brewer, pumps, …). Argument is 8 bit.
GB:
    Switches machine off. Any arguments?

    .. discovery missing for gc…gz
HZ: → hz:0100011100000,0291,00E9,0001,03FC,0543,3,100100,0000,00
    .. _HZ:

    Status information, comma-separated.

    0. Unknown bitfield. Bit 3 is one when milk pump(?) is on. Bit 6 is zero when brewing.
    1. Unknown
    2. Some kind of brewing sensor, 0xe8 when idle, goes up to ~0x255 when
       brewing.
    3. Flow meter(?), reset to 0 before new product is made
    4. Coffee heater temperature(?)
    5. Milk heater temperature(?)
    6. Brewer source/destination selection/encoder(?)
        3
            normal coffee
        5
            cappucino coffe
        6
            cappuccino milk
    7. Unknown bitfield
    8. Unknown
    9. Unknown
IC: →
    Read status from input board. No arguments.

    Bit 1…0
        Menu wheel on the left. State changes 00→01→11 or 11→10→00
        for each tick.
    Bit 8
        Somehow related to water tank
    Bit 10
        Stops toggling if coffee grounds bowl is full
KB: → kb:
    Unknown.
LS: → ls:0,1,1,0,0,0,0,0,0,0,0,0,3,0
    Unknown status information.
MA: → ok:
    Unknown, moves some part of the machine.
MJ: → ok:
    Dito.
MW: → ok:
    Dito.

    .. Milk?
OO: → oo:0,1,28,560,14
    Unknown status information.
PM: → ok:
    Play music. Easter egg.
RE:<address>
    .. _RE:

    Read from EEPROM at address. Argument is 16 bits and reads a single 16 bit
    word.
RM:<address>
    Read memory?
RT:<address>
    Reads a whole line (32 byte) from EEPROM, see RE_.
TL: → tl:R8Cx Loader V2.00
    Firmware loader version?
TY: → ty:EF516M V01.25
    Firmware version?
XX: → xx:F
    Unknown

Acknowledgements
----------------

The following people contributed to this project:

- Lars-Dominik Braun
- Lars Reinhardt
- Martin Flasskamp

This is not the first project interfacing with Jura’s debug interface. Notable
inspirations include:

- `Hacking the coffee machine <https://blog.q42.nl/hacking-the-coffee-machine-5802172b17c1>`_
- `Coffeemakers forum <https://www.coffeemakers.de/infocenter/forum/3-auslesen-der-logikeinheit/latest>`_

