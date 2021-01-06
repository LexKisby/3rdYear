"""
This model is PPM.  This essentially uses many order 1 
predictors, one for each letter in the alphabet.  Doing this
greatly clarifies the predictive abilities of the model.

Performance at order 1 is 20% smaller than order 0.
Performance at order 2 is 20% smaller than order 1.
Performance at order 3 is 8% smaller than order 2.
Performance at order 4 is -12% smaller than order 3.

Encoder overflow is handled by rescaling (by half), but
is eliminated in practice by the 30 bit encoder.
"""
from __future__ import print_function


""" 
Copyright 2012 Roger Flores

This file is part of Diz.

Diz is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Diz is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Diz.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import sys
import struct
from math import log

import arithmetic32 as arithmetic
from crc import Crc

order = 4

#import pdb
debug_file = None


def log2(n):
    return log(n, 2)


def c_string_encode(c):
    c = chr(c)
    if c == "\'":
        result = "'\\''"
    elif c == '\"':
        result = "\\\""
    elif ' ' < c <= '~':
        if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            result = "%s" % c
        else:
            result = "'%s'" % c
    elif c == ' ':
        result = "'\\s'"
    elif c == '\r':
        result = "'\\r'"
    elif c == '\n':
        result = "'\\n'"
    elif c == '\t':
        result = "'\\t'"
    else:
        result = '\\x%02X' % ord(c)

    return result


class Symbol():
    "Stats for a symbol"
    def __init__(self, symbol):
        self.symbol = symbol
        self.extent = 1


    def __str__(self):
        return c_string_encode(self.symbol) + ':' + str(self.extent)


    def __repr__(self):
        return     self.__str__()


class Model():
    "Model of symbols"
    def __init__(self, predictor=''):
        self.predictor = predictor
        self.symbols = []
        self.total = 0
        self.shorterPredictorModel = None


    def __str__(self):
        l = [s for s in self.symbols]
        l.sort(key=lambda i: i.extent, reverse=True)
        return str(len(self.symbols)) + '(' + str(self.total) + ') [' + \
            ', '.join([str(s) for s in l]) + ']'


    def __repr__(self):
        return     self.__str__()


class ModelAdaptiveEncode():
    """This class is just a container of static stats plus a function to estimate
    how likely the next symbol is using those stats"""

    def __init__(self, coded_file, clear_file, encoder, detailed_steps=0):
        self.step = 0
        self.detailed_steps = detailed_steps
        self.encoder = encoder
        self.__rescaled_from = 0

        # make a model
        self.predictor = ''
        self.model = None
        self.models = {}
        self.models[self.predictor] = self.__make_model()

        self.entropy = 1.0
        self.bits = 0.0


    def __rescale_counts(self, model):
        '''Because the stats are in a dict, they have no defined
        order, let alone one that matches the decoder.  This causes
        a problem when rescaling, because the order affects the
        low and high values.
        For now, convert to a list, order by low, rescale, then
        convert back to a dict.
        '''
        if model.total + 1 >= self.encoder.value_max:
            total = 0
            for c in model.symbols:
                extent = c.extent // 2
                if extent < 1:
                    extent = 1
                c.extent = extent
                total = total + extent

            model.symbols.sort(key=lambda i: i.symbol)
            model.symbols.sort(key=lambda i: i.extent, reverse=True)

            model.total = total


    def __make_model(self):
        model = Model()
        global debug_file
        if debug_file:
            debug_file.write("<h2>Model</h2>\n")
            debug_file.write("<p>PPMC model using " + str(order) + " symbol predictor.</p>\n")
            debug_file.write("<p>30 bit encoder.</p>\n")

        return model


    def push(self, value):
        global debug_file
        if debug_file and self.step < self.detailed_steps:
            debug_file.write("<model>")

        # find the model
        self.step = self.step + 1
        escape = None

        # find the model with the longest predictor
        predictor = self.predictor
        while predictor not in self.models:
            predictor = predictor[1:]

        model = self.models[predictor]
        exclusions = []


        while model != None:
            esc_estimate = max(len(model.symbols), 1)
            total = model.total + esc_estimate
            if exclusions:
                for c in model.symbols:
                    if c.symbol in exclusions:
                        total = total - c.extent

                # sometimes models have all symbols excluded.
                if total == esc_estimate:
                    model = model.shorterPredictorModel
                    continue

            # find value in model
            low = 0
            found = None
            for c in model.symbols:
                if c.symbol not in exclusions:
                    high = low + c.extent
                    if c.symbol == value:
                        found = c
                        self.encoder.encode(value, low, high, total)
                        if debug_file:
                            self.entropy = self.entropy * float(high - low) / (total)
                            self.bits = self.bits + -log2(float(high - low) / (total))
                            if self.step < self.detailed_steps:
                                debug_file.write(" <v>'{0:s}':{1:d}/{2:d}</v>".format(model.predictor, low, total))
                        model = None
                        break

                    low = high


            if not found:
                escape = value
                extent = esc_estimate
                high = low + extent

                self.encoder.encode(value, low, high, total)
                if debug_file:
                    self.entropy = self.entropy * float(high - low) / (total)
                    self.bits = self.bits + -log2(float(high - low) / (total))
                    if self.step < self.detailed_steps:
                        debug_file.write(" <v class='esc'>'{0:s}':{1:d}/{2:d}</v>".format(model.predictor, low, total))

                for s in model.symbols:
                    exclusions.append(s.symbol)
                model = model.shorterPredictorModel


        if not found:
            self.encoder.encode(value, value, value + 1, 256)
            if debug_file:
                self.entropy = self.entropy * float(1) / (256)
                self.bits = self.bits + -log2(float(1) / (256))
                if self.step < self.detailed_steps:
                    debug_file.write(" <v class='esc new'>{0:d}/{1:d}</v>".format(value, 256))

        self.update(value, low, high, escape)

        if order > 0:
            if len(self.predictor) >= order:
                self.predictor = self.predictor[1:] + chr(value)
            else:
                self.predictor = self.predictor + chr(value)

        if debug_file and self.step < self.detailed_steps:
            debug_file.write("</model>")


    def update(self, value, low, high, escape):
        # find the model with the longest predictor
        # create all those missing
        predictor = self.predictor
        new_model = None
        while predictor not in self.models:
            model = self.models[predictor] = Model(predictor)
            if new_model:
                new_model.shorterPredictorModel = model
            new_model = model
            predictor = predictor[1:]

        if new_model:
            new_model.shorterPredictorModel = self.models[predictor]
        model = self.models[self.predictor]


        # update models
        symbol = value if escape == None else escape
        while model != None:
            found = None
            for s in model.symbols:
                if s.symbol == symbol:
                    s.extent = s.extent + 1
                    found = s
                    break
            if found == None:
                s = Symbol(symbol)
                model.symbols.append(s)

            model.total = model.total + 1
            self.__rescale_counts(model)

            model = model.shorterPredictorModel


    def dump(self):
        l = []
        for k,v in self.models.items():
            l.append((k, v))

        l.sort(key=lambda i: i[0][::-1])
        #l.sort(key=lambda i: i[1].total, reverse=True)
        for i in l:
            print("{0:->4s}: {1:s}".format(i[0], i[1]))


class ModelAdaptiveDecode():
    "This class is just a container of static stats plus a function to estimate how likely the next symbol is using those stats"
    def __init__(self, clear_file, coded_file, decoder, detailed_steps=0):
        self.decoder = decoder
        self.decoder_value, self.decoder_extent = decoder.decode(None, None, None)

        self.predictor = ''
        self.model = None
        self.models = {}
        self.models[self.predictor] = self.__read_model(clear_file, coded_file)
        self.step = 0
        self.detailed_steps = detailed_steps
        self.entropy = 1.0
        #self.check()


    def __read_model(self, clear_file, coded_file):
        # read the model of all the data
        model = Model()

        global debug_file
        if debug_file:
            debug_file.write("<h2>Model</h2>\n")
            debug_file.write("<p>PPMC model using " + str(order) + " symbol predictor.</p>\n")
            debug_file.write("<p>30 bit encoder.</p>\n")

        return model


    def __rescale_counts(self, model):
        if model.total + 1 >= self.decoder.value_max:
            total = 0
            for c in model.symbols:
                extent = c.extent // 2
                if extent < 1:
                    extent = 1
                c.extent = extent
                total = total + extent

            model.symbols.sort(key=lambda i: i.symbol)
            model.symbols.sort(key=lambda i: i.extent, reverse=True)

            model.total = total


    def pull(self):
        global debug_file
        if debug_file and self.step < self.detailed_steps:
            debug_file.write("<model>")

        assert(self.decoder_value < self.decoder_extent)

        self.step = self.step + 1

        # find the model with the longest predictor
        predictor = self.predictor
        while predictor not in self.models:
            predictor = predictor[1:]

        model = self.models[predictor]
        exclusions = []


        while model != None:
            esc_estimate = max(len(model.symbols), 1)
            total = model.total + esc_estimate
            if exclusions:
                for c in model.symbols:
                    if c.symbol in exclusions:
                        total = total - c.extent

                # sometimes models have all symbols excluded.
                if total == esc_estimate:
                    model = model.shorterPredictorModel
                    continue

            # find decoder_value in model
            found = None
            symbol = None
            escape = None
            code = self.decoder_value * (total) // self.decoder_extent
            if code < total - esc_estimate:
                low = 0
                for c in model.symbols:
                    if c.symbol not in exclusions:
                        high = low + c.extent
                        if low + c.extent > code >= low:
                            found = c
                            symbol = c.symbol
                            #if type(symbol) == int:
                            #    symbol = chr(symbol)

                            self.decoder_value, self.decoder_extent = \
                                self.decoder.decode(low, high, total)
                            if debug_file:
                                self.entropy = self.entropy * float(high - low) / (total)
                                if self.step < self.detailed_steps:
                                    debug_file.write(" <v>'{0:s}':{1:d}/{2:d}</v>".format(model.predictor, low, total))
                            model = None
                            break

                        low = high

            if not found:
                low = total - esc_estimate
                extent = esc_estimate
                high = low + extent
                self.decoder_value, self.decoder_extent = \
                    self.decoder.decode(low, high, total)
                if debug_file and self.step < self.detailed_steps:
                    debug_file.write(" <v class='esc'>'{0:s}':{1:d}/{2:d}</v>".format(model.predictor, low, total))

                for s in model.symbols:
                    exclusions.append(s.symbol)
                model = model.shorterPredictorModel

        if not found:
            symbol = self.push()
            escape = symbol

        self.update(symbol, low, high, escape)

        if order > 0:
            if len(self.predictor) >= order:
                self.predictor = self.predictor[1:len(self.predictor)] + chr(symbol)
            else:
                self.predictor = self.predictor + chr(symbol)

        if debug_file and self.step < self.detailed_steps:
            debug_file.write("</model>")

        return symbol


    def update(self, value, low, high, escape):
        # find the model with the longest predictor
        # create all those missing
        predictor = self.predictor
        new_model = None
        while predictor not in self.models:
            model = self.models[predictor] = Model(predictor)
            if new_model:
                new_model.shorterPredictorModel = model
            new_model = model
            predictor = predictor[1:]

        if new_model:
            new_model.shorterPredictorModel = self.models[predictor]
        model = self.models[self.predictor]


        # update models
        symbol = value if escape == None else escape
        while model != None:
            found = None
            for s in model.symbols:
                if s.symbol == symbol:
                    s.extent = s.extent + 1
                    found = s
                    break
            if found == None:
                s = Symbol(symbol)
                model.symbols.append(s)

            model.total = model.total + 1
            self.__rescale_counts(model)

            model = model.shorterPredictorModel


    def push(self):
        symbol = (self.decoder_value * 256) // self.decoder_extent

        '''
        for s in self.model.symbols:
            if s.symbol == symbol:
                raise IOError("value %s already in model" % symbol)
        '''

        self.decoder_value, self.decoder_extent = \
            self.decoder.decode(symbol, symbol + 1, 256)
        global debug_file
        if debug_file and self.step < self.detailed_steps:
            debug_file.write(" <v class='esc new'>{0:d}/{1:d}</v>".format(symbol, 256))

        return symbol


class codec():

    def init_debug_file(self, debug_file):
        debug_file.write("<!DOCTYPE html>")
        debug_file.write("<html lang='en'>")
        debug_file.write("<head>")
        debug_file.write("<meta charset='utf-8' />")
        debug_file.write("<style type='text/css'>\n")
        debug_file.write("data {display: block; }\n")
        #debug_file.write("v {width: 6em; text-align: right; padding: 2px; display: block; float: left; }\n")
        debug_file.write("v {width: 6em; text-align: right; padding: 2px; }\n")
        debug_file.write("v.bin { width: 16em; }\n")
        debug_file.write("v.esc { background-color: #CFECEC; }\n")
        debug_file.write("v.new { color: red; }\n")
        debug_file.write("data:hover { background-color: yellow; }\n")
        debug_file.write("</style>")
        debug_file.write("</head>")
        debug_file.write("<body>")

    def finish_debug_file(self, debug_file):
        debug_file.write("</body>")
        debug_file.write("</html>")



    def encode(self, out_file, in_file, size, progress=None, debug=True):
        global debug_file
        if debug:
            debug_name = os.path.splitext(in_file.name)[0] + '_enc_trace' + '.' + 'htm'
            debug_file = open(debug_name, "w")
            self.init_debug_file(debug_file)
        step = 0
        detailed_steps = 8000
        percent = -1

        encoder = arithmetic.Encoder(out_file, detailed_steps)
        encoder.debug_file = debug_file
        model = ModelAdaptiveEncode(out_file, in_file, encoder, detailed_steps)
        if debug_file:
            debug_file.write("<h2>Encode</h2>\n")
            if detailed_steps > 0:
                debug_file.write("<pre>\n")

        crc = Crc()
        while True:
            value = in_file.read(1)
            if not value:
                break
            value = ord(value)
            crc.add(value)
            
            if progress:
                percent_new = step // (size // 100);
                if percent_new != percent:
                    print('encoded {0}%'.format(percent_new), end='\r')
                    sys.stdout.flush()
                    percent = percent_new
            
            if debug_file:
                if step < detailed_steps:
                    debug_file.write("<data>")
                    debug_file.write("%d." % step)
                    debug_file.write("<v>%s</v>" % c_string_encode(value))

            model.push(value)

            if debug_file:
                if step < detailed_steps:
                    debug_file.write(" </data>\n")
            step = step + 1


        encoder.flush()
        crc.write(out_file)

        if debug_file:
            if detailed_steps > 0:
                debug_file.write("</pre>\n")
            debug_file.write("<h2>Performance</h2>\n")
#            debug_file.write("<p>entropy is %f</p>\n" % log2(model.entropy))
            debug_file.write("<p>Model bits used is %f (%f bytes)</p>\n" % (model.bits, model.bits / 8))
            debug_file.write("<p>bits used is %d</p>\n" % encoder.length())
            if step > 0:
                debug_file.write("<p>Used %f bits per symbol.</p>\n" % (float(encoder.length()) / step))

            self.finish_debug_file(debug_file)
            debug_file.close()

        if progress:
            print('encoded 100% ')
            
        return model.models['']


    def decode(self, out_file, in_file, size, progress=None, debug=True):
        global debug_file
        if debug:
            debug_name = os.path.splitext(in_file.name)[0] + '_dec_trace' + '.' + 'htm'
            debug_file = open(debug_name, "w")
            self.init_debug_file(debug_file)
        step = 0
        detailed_steps = 8000
        percent = -1
        percent_size = size // 100
        if progress:
            print()

        try:
            decoder = arithmetic.Decoder(in_file, detailed_steps)
            decoder.debug_file = debug_file
            model = ModelAdaptiveDecode(out_file, in_file, decoder, detailed_steps)

            if debug_file:
                debug_file.write("<h2>Decode</h2>\n")
                if detailed_steps > 0:
                    debug_file.write("<pre>\n")

            crc = Crc()
            while size > 0:
                if debug_file:
                    if step < detailed_steps:
                        debug_file.write("<data>")
                        debug_file.write("%d." % step)

                symbol = model.pull()
                out_file.write(struct.pack("B", symbol))
                crc.add(symbol)

                size = size - 1
            
                if progress:
                    percent_new = step // percent_size
                    if percent_new != percent:
                        print('decoded {0}%'.format(percent_new), end='\r')
                        sys.stdout.flush()
                        percent = percent_new

                if debug_file:
                    if step < detailed_steps:
                        debug_file.write("<v>%s</v>" % c_string_encode(symbol))
                        debug_file.write(" </data>\n")
                step = step + 1


            if debug_file:
                if detailed_steps > 0:
                    debug_file.write("</pre>\n")

            decoder.flush()
            crc.match(in_file)

            if progress:
                print('encoded 100% ')

        finally:
            if debug_file:
                self.finish_debug_file(debug_file)
                debug_file.close()
