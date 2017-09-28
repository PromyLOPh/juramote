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

import logging

from .com import *

log = logging.getLogger(__name__)

class Recipe:
    """
    Abstract recipe interface.
    """

    name = None

    def __call__ (self, machine):
        assert self.commands

        def wait (t):
            time.sleep (t)
            return True

        f = {'pressButton': machine.pressButton, 'wait': wait}
        for cmd, args in self.commands:
            log.debug ('{} {}'.format (cmd, args))
            if not f[cmd] (*args):
                return False
        return True

    @staticmethod
    def dial (machine, default, value, step):
        """
        Use up/down dial to increase/decrease current value
        """
        if value >= default:
            return [('pressButton', [machine.buttons.FORWARD])] * ((value - default)//step)
        else:
            return [('pressButton', [machine.buttons.BACK])] * ((default - value)//step)

# default bei alacarte: 1 bohne, 150ml

class CoffeeRecipe (Recipe):
    name = 'coffee'
    # min, base, max, step
    strength = (1, 4, 5, 1)
    amount = (100, 150, 500, 5) # ml

    def __init__ (self, machine, strength=strength[1], amount=amount[1]):
        if not (self.strength[0] <= strength <= self.strength[2]):
            raise ValueError ('strength must be between {} and {}'.format (self.strength[0], self.strength[2]))
        if not (self.amount[0] <= amount <= self.amount[2]):
            raise ValueError ('amount must be between {} and {} ml'.format (self.amount[0], self.amount[2]))

        self.commands = []
        self.commands.extend ([('pressButton', [machine.machine.buttons.COFFEE])])
        self.commands.extend (self.dial (machine.machine, self.strength[1], strength, self.strength[3]))
        # XXX: measure time?
        self.commands.append (('wait', [12]))
        self.commands.extend (self.dial (machine.machine, self.amount[1], amount, self.amount[3]))

class CappuccinoRecipe (Recipe):
    name = 'cappuccino'
    # min, base, max
    strength = (1, 4, 5, 1)
    amount = (100, 150, 500, 5) # ml, XXX default correct?
    milk = (19, 19, 100, 1) # seconds

    def __init__ (self, machine, strength=strength[1], amount=amount[1], milk=milk[1]):
        if not (self.strength[0] <= strength <= self.strength[2]):
            raise ValueError ('strength must be between {} and {}'.format (self.strength[0], self.strength[2]))
        if not (self.amount[0] <= amount <= self.amount[2]):
            raise ValueError ('amount must be between {} and {} ml'.format (self.amount[0], self.amount[2]))
        if not (self.milk[0] <= milk <= self.milk[2]):
            raise ValueError ('milk must be between {} and {} s'.format (self.milk[0], self.milk[2]))

        self.commands = []
        self.commands.extend ([('pressButton', [machine.machine.buttons.CAPPUCCINO])])
        self.commands.extend (self.dial (machine.machine, self.strength[1], strength, self.strength[3]))
        self.commands.append (('wait', [12]))
        self.commands.extend (self.dial (machine.machine, self.milk[1], milk, self.milk[3]))
        self.commands.append (('wait', [31]))
        self.commands.extend (self.dial (machine.machine, self.amount[1], amount, self.amount[3]))

recipes = {
    'coffee': CoffeeRecipe,
    'cappuccino': CappuccinoRecipe,
    }

