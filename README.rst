juramote
========

Remote control for Jura coffee maker Xs90 (EF516M V01.25).

Usage
-----

The software works on any machine running Python, but using a Raspberry Pi
(Zero W) is recommended. Standard pip install procedure is supported::

    pip install .

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
    Unknown.
CS: → cs:03EC0562300E800000000000000600601C1
    Unknown.
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
    Unknown status information.
IC: →
    Read status from input board. No arguments.
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

