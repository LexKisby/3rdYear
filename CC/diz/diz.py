"""
This is a file compressor/decompressor.


Examples:
    diz foo.txt
        Compress foo.txt to foo.diz
    diz foo.diz
        Decompress foo.diz to foo.txt

Options:
    -t test by decompressing
    -o name the output file

Note we avoid working with collections of files.  That problem requires
creating a packaging system like tar whereas this is focusing on compression.

There is no codec in this file.  A variety of codecs are handled by
codec_manager.py.  You can add your own codec to it.

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
from stat import ST_SIZE
import sys
import struct
import time
import gc

import codec_manager

#import pdb

# A magic value is needed to identify data written by this app.  Data with this
# magic value in it was probably by this app, and data without it probably was
# not. Substitute in your unique four characters to identify your files
magic_value = "DIZ1"

# A version in the data file lets you know which version of your algorithm
# produced the data. You want to be able to change your algorithm without
# destroying old data, and this let's you do that safely.
version = {"major": 1, "minor": 0}

# many systems commonly put type information in the file's name extension.  This
# is the extension used by this app.
extension = "diz"

#    pdb.set_trace()


class UsageError(Exception):
    pass


def print_about(name):
    print("DIZ (Dizzy) - Diz Isn't Zip")


def print_version():
    message = "version %d" % version["major"]
    if version["minor"] != 0:
        message = message + ".%d" % version["minor"]

    print(message)


def print_usage(name=os.path.basename(sys.argv[0])):
    print_about(name)
    print_version()
    print("Encode or decode a file.", file=sys.stderr)
    print("Usage: %s infile (compress infile to infile.diz)" % name, file=sys.stderr)
    print("Usage: %s infile.%s (decompress infile.%s)" % (name, extension, extension), file=sys.stderr)
    print("Usage: %s -t infile.%s (compress infile and decompress a copy)" % (name, extension), file=sys.stderr)
    print("Usage: %s infile.%s -o outfile (decompress infile.%s to outfile)" % (name, extension, extension), file=sys.stderr)
    print("Usage: %s -d infiles (compress and output a trace file)" % (name), file=sys.stderr)


def encode_file(out_name, in_name, progress, debug):
    encode_complete = False

    out_file = open(out_name, "wb")
    in_file = open(in_name, "rb")

    try:
        # write the header
        file_header = struct.pack("<4s B B", magic_value, version["major"], version["minor"])
        out_file.write(file_header)

        # now write the file (name + size + data)
        in_file_size = os.stat(in_name)[ST_SIZE]
        out_file.write(in_name)
        out_file.write('\0')
        out_file.write(struct.pack("<L", in_file_size))

        codec_manager.encode(out_file, in_file, in_file_size, None, progress, debug = debug)
        encode_complete = True

    finally:
        in_file.close()
        out_file.close()

#    if not encode_complete:
#        os.remove(out_name)


def read_until_char(src_file, char_to_stop):
    string_read = ""
    while True:
        c = src_file.read(1)
        if c == char_to_stop or not c:
            return string_read

        string_read = string_read + c


def decode_file(out_name, in_name, progress, debug):
    in_file = open(in_name, "rb")
    validate_header_in_file(in_file)
    try:
        while in_file.tell() < os.stat(in_name)[ST_SIZE]:
            # format is name + size + data
            in_file_original_name = read_until_char(in_file, '\0')
            if not out_name:
                # if the original file still exists, refuse to overwrite it, unless
                # it was explicitly named
                if os.path.exists(in_file_original_name):
                    raise IOError("%s file exists." % in_file_original_name)

                out_name = in_file_original_name

            in_file_size = struct.unpack("<L", in_file.read(4))[0]

            out_file = open(out_name, "wb")
            codec_manager.decode(out_file, in_file, in_file_size, progress, debug = debug)
            out_file.close()

    finally:
        in_file.close()


def validate_header_in_file(test_file):
    header_block = test_file.read(4 + 1 + 1)

    # validate
    if magic_value != header_block[0:4]:
        raise IOError("Not a valid file.")

    # check the version
    (version_major, version_minor) = struct.unpack("BB", header_block[4:4 + 2])
    if version_major != version["major"]:
        raise IOError("Not a valid version (version {0} found but version {1} was expected).".format(version_major, version["major"]))


def validate_file(name):
    original_name = None
    test_file = open(name, "rb")

    try:
        validate_header_in_file(test_file)
        original_name = read_until_char(test_file, '\0')
    finally:
        test_file.close()

    return original_name


def is_filename(name):
    return name[0] != '-'


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        if len(argv) < 2:
            raise UsageError

        args = argv[1:]

        test = False
        if '-t' in args:
            test = True
            args.remove('-t')

        debug = False
        if '-d' in args:
            debug = True
            args.remove('-d')

        progress = None
        if '-p' in args:
            progress = 'percent'
            args.remove('-p')

        if not is_filename(args[0]):
            raise UsageError

        file_name = args[0]

        # Support "foo" meaning "foo.diz" when "foo" does not exist.
        if not os.path.isfile(file_name) and \
            os.path.splitext(file_name)[1] == '':
            file_name = file_name + '.' + extension

        if not os.path.exists(file_name) or not os.path.isfile(file_name):
            raise IOError("The file '%s' is not found." % file_name)

        source_name = None
        encoded_name = None
        dest_name = None
        try:
            dest_name = validate_file(file_name)
        except IOError as msg:
            # file_name is not a valid file to decompress, so compress it
            source_name = file_name
            encoded_name = os.path.splitext(file_name)[0] + '.' + extension
            start_time = time.time()
            encode_file(encoded_name, source_name, progress, debug)
            if test:
                print('{:,} secs '.format(int(time.time() - start_time)), end='')
                dest_name = file_name

                # collect before decoding adds a lot more garbage
                gc.collect()

        if dest_name:
            # adding "-o foo.txt" sends the decoded stream to foo.txt instead
            # of to the original name.
            # Directory names are not handled
            if len(args) > 1 and args[1] == "-o":
                if len(args) > 2:
                    if os.path.splitext(args[2])[1] != '':
                        dest_name = args[2]
                    else:
                        dest_name = os.path.splitext(args[2])[0] + \
                            os.path.splitext(dest_name)[1]

                    
                else:
                    raise UsageError

            elif test:
                dest_name = os.path.split(dest_name)
                dest_name = os.path.join(dest_name[0], 'Copy of {0}'.format(dest_name[1]))

            if not encoded_name:
                encoded_name = file_name
            start_time = time.time()
            decode_file(dest_name, encoded_name, progress, debug)
            if test:
                print('{:,} secs'.format(int(time.time() - start_time)))

    except UsageError:
        print_usage()
        return 2        # 2 means command line error

    except IOError as msg:
        print(msg, file=sys.stderr)
        return 1        # 1 means general error

    return 0

if __name__ == "__main__":
    sys.exit(main())
