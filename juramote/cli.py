# Copyright 2017 juramote contributors (see README)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .com import *

class Cli:
    def __init__ (self):
        self.parser = argparse.ArgumentParser (description='Control Jura coffee maker through debug port.')
        self.parser.add_argument('--tty', '-t', default='/dev/ttyUSB0', help='Serial port')
        self.parser.add_argument('--verbose', '-v', action='store_true', help='Print debugging messages')
        subparsers = self.parser.add_subparsers (title='subcommands')
        for name, func in [('info', self.doInfo), ('input', self.doInput)]:
            p = subparsers.add_parser(name, help=func.__doc__)
            p.set_defaults(func=func)

        p = subparsers.add_parser ('button', help=self.doButton.__doc__)
        p.add_argument('name', help='Button name')
        p.set_defaults(func=self.doButton)

        p = subparsers.add_parser ('eeprom', help=self.doEeprom.__doc__)
        p.add_argument('address', type=int, nargs='?', help='Read single word')
        p.set_defaults(func=self.doEeprom)

        p = subparsers.add_parser ('fn', help=self.doFn.__doc__)
        p.add_argument('name', help='Button name')
        p.set_defaults(func=self.doFn)

        p = subparsers.add_parser ('display', help=self.doDisplay.__doc__)
        p.add_argument('-d', '--default', action='store_true', help='Change default message text.')
        p.add_argument('value', nargs='*', help='String to be displayed or empty for reset.')
        p.set_defaults(func=self.doDisplay)

    def run (self):
        args = self.parser.parse_args ()
        if args.verbose:
            logging.basicConfig (level=logging.DEBUG)
        if getattr (args, 'func', None):
            machine = Raw (args.tty)
            return args.func (machine, args)
        else:
            self.parser.print_usage ()
            return 1

    def doInfo (self, machine, args):
        """
        Display machine status
        """
        data = {'type': machine.getType ().decode ('ascii'), 'counter': {}}
        for name, member in ImpressaXs90Eeprom.__members__.items():
            if name.startswith ('COUNT_'):
                data['counter'][name[6:]] = machine.readEeprom (member)
        json.dump (data, sys.stdout, indent=4)

    def doEeprom (self, machine, args):
        """
        Dump EEPROM
        """
        if args.address is not None:
            print (hex (machine.readEeprom (args.address)))
        else:
            data = []
            for offset in range (0, machine.EEPROM_LINES):
                data.append (codecs.encode (machine.readEepromLine (offset*(machine.EEPROM_LINELENGTH//machine.EEPROM_WORDLENGTH)), 'hex').decode ('ascii'))
            json.dump (data, sys.stdout, indent=4)

    def doDisplay (self, machine, args):
        """
        Print text on display
        """
        if args.value:
            if args.default:
                return machine.printDisplayDefault (' '.join (args.value))
            else:
                return machine.printDisplay (' '.join (args.value))
        else:
            return machine.resetDisplay ()

    def doInput (self, machine, args):
        """
        Read sensors
        """
        print (machine.readInput ())

    def doButton (self, machine, args):
        """
        Press a button
        """
        try:
            i = int (args.name)
        except ValueError:
            i = getattr (ImpressaXs90Buttons, args.name.upper ())

        print (machine.pressButton (i))

    def doFn (self, machine, args):
        i = int (args.name, 16)
        # 13 brewgroup position ausleeren, error 8
        machine._send ('FN:{:02X}'.format (i).encode ('ascii'))
        print (machine._receiveBool ())
        return True

def main ():
    cli = Cli ()
    cli.run ()

