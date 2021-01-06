"""
This codec manager calls the codec chosen to encode or decode.  
When encoding, the chosen codec passed in by name is used.  The chosen codec's
id is written to the out_file.  When decoding, the codec's id is read from in_file and
used.  Codecs do not know anything about each other or this manager.
"""


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


import codec_pass
#import codec_arith_short
#import codec_arith_trad
#import codec_adaptive
import codec_ppm
#import codec_ppmoa

# This is the list of known codecs.  Add new ones to this list for use
codecs = [
    # id, codec (must be imported), name (string)
    [0, codec_pass.codec, "pass"],
#    [1, codec_arith_short.codec, "arith"],
#    [2, codec_arith_trad.codec, "trad"],
#    [3, codec_adaptive.codec, "adaptive"],
    [4, codec_ppm.codec, "ppm"],
#    [5, codec_ppmoa.codec, "ppmoa"]
]
codec_default = "ppm"


def encode(out_file, in_file, size, method=None, progress=None, debug=False):
    global codecs
    global codec_default
    if method == None: method =  codec_default
    for c in codecs:
        if method == c[2]:
            out_file.write(chr(ord('a') + c[0]))
            codec = c[1]()
            codec.encode(out_file, in_file, size, progress, debug)
            return
    
    raise IOError("Unknown codec (%s) used." % method)


def decode(out_file, in_file, size, progress=None, debug=False):
    global codecs
    method =  ord(in_file.read(1)) - ord('a')
    for c in codecs:
        if method == c[0]:
            codec = c[1]()
            codec.decode(out_file, in_file, size, progress, debug)
            return
    
    raise IOError("Unknown codec (%c) used." % chr(ord('a') + method))

