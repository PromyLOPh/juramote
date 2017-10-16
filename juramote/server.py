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

from flask import Flask, request, abort
from flask.json import jsonify
from functools import wraps
from wtforms import Form, IntegerField, validators
from hashlib import sha512
import time

from .com import *
from .recipes import *

class DefaultConfig:
    TTY_PATH = '/dev/ttyUSB0'

app = Flask(__name__)
app.config.from_object('juramote.server.DefaultConfig')
app.config.from_envvar('JURAMOTE_SETTINGS')
machine = Stateful (app.config['TTY_PATH'])
if app.config['DEBUG']:
    logging.basicConfig (level=logging.DEBUG)

def authenticated (permission):
    """
    API key is required
    """
    def wrapper (f):
        @wraps(f)
        def decorator(*args, **kwargs):
            key = request.headers.get ('X-API-Key')
            if not key:
                abort (401)
            d = sha512 (key.strip ().encode ('utf8')).hexdigest ()
            if permission not in app.config['API_KEYS'].get (d):
                abort (401)
            return f(*args, **kwargs)
        return decorator
    return wrapper

@app.route ('/v1/raw/eeprom', methods=['GET'])
@authenticated('rraw')
def rawEepromFull ():
    data = []
    for offset in range (0, machine.EEPROM_LINES):
        data.append (codecs.encode (machine.readEepromLine (offset*(machine.EEPROM_LINELENGTH//machine.EEPROM_WORDLENGTH)), 'hex').decode ('ascii'))
    return jsonify (status='ok', response=data)

@app.route ('/v1/raw/eeprom/<int:address>', methods=['GET'])
@authenticated('rraw')
def rawEeprom (address):
    return jsonify (status='ok', response=machine.readEeprom (address))

@app.route ('/v1/raw/eeprom/<int:address>', methods=['POST'])
@authenticated('wraw')
def rawWriteEeprom (address):
    return jsonify (status='ok', response=machine.writeEeprom (address, int (request.form['value'])))

@app.route ('/v1/raw/eeprom/line/<int:address>', methods=['GET'])
@authenticated('rraw')
def rawEepromLine (address):
    return jsonify (status='ok', response=machine.readEepromLine (address))

@app.route ('/v1/raw/input', methods=['GET'])
@authenticated('rraw')
def rawInput ():
    return jsonify (status='ok', response=machine.readInput ())

@app.route ('/v1/raw/display/permanent', methods=['POST'])
@authenticated('wraw')
def rawDisplayPermanent ():
    return jsonify (status='ok', response=machine.printDisplay (request.form['text']))

@app.route ('/v1/raw/display/default', methods=['POST'])
@authenticated('wraw')
def rawDisplayDefault ():
    return jsonify (status='ok', response=machine.printDisplayDefault (request.form['text']))

@app.route ('/v1/raw/display/reset', methods=['POST'])
@authenticated('wraw')
def rawDisplayReset ():
    return jsonify (status='ok', response=machine.resetDisplay ())

@app.route ('/v1/raw/button', methods=['POST'])
@authenticated('wraw')
def rawButton ():
    return jsonify (status='ok', response=machine.pressButton (int (request.form['name'])))

@app.route ('/v1/raw/command', methods=['POST'])
@authenticated('wraw')
def rawCommand ():
    try:
        return jsonify (status='ok', response=machine.raw (request.form['cmd']))
    except ValueError:
        abort (504)

# high-level API
@app.route ('/v1/firmware', methods=['GET'])
@authenticated('r')
def firmware ():
    data = {'type': machine.getType (), 'loader': machine.getLoader ()}
    return jsonify (status='ok', response=data)

@app.route ('/v1/counter', methods=['GET'])
@authenticated('r')
def counter ():
    try:
        data = {}
        for name, member in machine.machine.eeprom.__members__.items():
            if name.startswith ('COUNT_'):
                data[name[6:]] = machine.readEeprom (member)
    except ValueError:
        abort (500)
    return jsonify (status='ok', response=data)

@app.route ('/v1/status', methods=['GET'])
@authenticated('r')
def status ():
    # TODO: flow meter, temperatures
    data = {'state': machine.getState ().name}
    return jsonify (status='ok', response=data)

@app.route ('/v1/product', methods=['GET'])
@authenticated('r')
def listProducts ():
    return jsonify (status='ok', response=list (recipes.keys ()))

class CoffeeForm (Form):
    strength = IntegerField (validators=[validators.NumberRange (CoffeeRecipe.strength[0], CoffeeRecipe.strength[2])])
    amount = IntegerField (validators=[validators.NumberRange (CoffeeRecipe.amount[0], CoffeeRecipe.amount[2])])

class CappuccinoForm (Form):
    strength = IntegerField (validators=[validators.NumberRange (CappuccinoRecipe.strength[0], CappuccinoRecipe.strength[2])])
    amount = IntegerField (validators=[validators.NumberRange (CappuccinoRecipe.amount[0], CappuccinoRecipe.amount[2])])
    milk = IntegerField (validators=[validators.NumberRange (CappuccinoRecipe.milk[0], CappuccinoRecipe.milk[2])])

productForms = {
    'coffee': CoffeeForm,
    'cappuccino': CappuccinoForm,
    }

# XXX: replace with Stateful state reading (ic:)
productInProgress = Lock ()

@app.route ('/v1/product/<name>', methods=['POST'])
@authenticated('w')
def makeProduct (name):
    if name not in recipes:
        abort (404)
    form = productForms[name] (request.form)
    if form.validate ():
        with productInProgress:
            if name == 'coffee':
                r = recipes[name] (machine, form.strength.data, form.amount.data)
            elif name == 'cappuccino':
                r = recipes[name] (machine, form.strength.data, form.amount.data, form.milk.data)
            if r (machine):
                return jsonify (status='ok')
            else:
                abort (500)
    abort (500)

# error handler
@app.errorhandler(405)
def invalidMethod (e):
    return jsonify (status='invalidMethod'), 405

@app.errorhandler(404)
def notFound (e):
    return jsonify (status='notFound'), 404

@app.errorhandler(401)
def permissionDenied (e):
    return jsonify (status='permissionDenied'), 401

@app.errorhandler(500)
def serverError (e):
    return jsonify (status='serverError'), 500

@app.errorhandler(504)
def serverError (e):
    return jsonify (status='timeout'), 504

def main ():
    app.run(debug=True)

