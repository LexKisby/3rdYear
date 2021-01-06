"""
Accumulate values to form a crc, and then either write it or read one
to match it.

The crc value is preceded by a magic value.  Sometimes the crc value
wasn't where it was expected, and the magic value identifies that case
instead of confusing it with a mismatched crc value.
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


import struct

from binascii import crc32

class Crc():
    """Accumulates values and then writes or matches the value."""

    def __init__(self):
        self.value = 0

    def add(self, value):
        self.value = crc32(struct.pack("B", value), self.value) & 0xffffffff

    def write(self, out_file):
        out_file.write(struct.pack("<H", 0xc8c0))
        out_file.write(struct.pack("<L", self.value))
        self.value = None

    def match(self, in_file):
        # crc check
        crc_id = struct.unpack("<H", in_file.read(2))[0]
        # FIXME sometimes the encoder writes more bits than the
        # decoder reads (an overflow bit - test case is a zero byte file).
        # in that case, read one more byte to reach the header
        if crc_id == 0xc000:
            crc_id = (struct.unpack("<B", in_file.read(1))[0] << 8) + 0xc0
        if crc_id != 0xc8c0:
            raise IOError("crc value not found (%4X)" % crc_id)
        orig_crc = struct.unpack("<L", in_file.read(4))[0]
        if self.value != orig_crc:
            raise IOError("crc values mismatch (%06X vs. %06X)." % (orig_crc, self.value))
        self.value = None
