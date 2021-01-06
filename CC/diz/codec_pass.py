"""
This is the base codec.  It simply passes the data through, unmodified. 
So it's simple and complete, but minimally useful.

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


class codec():
    
    def encode(self, out_file, in_file):
        # every byte read is immediately written unmodified
        while True:
            value = in_file.read(1)
            if not value:
                break
            out_file.write(value)
    
    
    def decode(self, out_file, in_file, size):
        # every byte read is immediately written unmodified
        while size > 0:
            value = in_file.read(1)
            out_file.write(value)
            
            size = size - 1
    
