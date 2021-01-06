"""
The encoder is a traditional arithmetic 30bit encoder, 
outputting one bit at a time.
"""


import struct

#import pdb

write_buffer = 0
write_count = 0

def write_bit(out_file, bit):
    """write a bit to a file
    
    The bits are buffered into a byte.  If less than a byte is filled, then 
    flush_bits() should be called to insure all bits are written.
    """
    global write_buffer
    global write_count

    write_buffer = (write_buffer << 1) | bit
    write_count = write_count + 1
    if write_count >= 8:
        assert(write_count == 8)
        out_file.write(struct.pack("<B", write_buffer))
        write_buffer = 0
        write_count = 0



def flush_bits(out_file):
    global write_buffer
    global write_count
    
    if write_count > 0:
        out_file.write(struct.pack("<B", write_buffer << (8 - write_count)))
        write_buffer = 0
        write_count = 0
    
    
read_buffer = 0
read_count = 0


def read_bit(in_file):
    """write a bit to a file
    
    The bits are buffered into a byte.  If less than a byte is filled, then 
    flush_bits() should be called to insure all bits are written.
    """
    global read_buffer
    global read_count
    
    if read_count == 0:
        v = in_file.read(1)
        if len(v) > 0:
            read_buffer = struct.unpack("<B", v)[0]
        else:
            read_buffer = 0
        read_count = 8

    bit = (read_buffer >> (read_count - 1)) & 1
    read_count = read_count - 1
            
    return bit
    
    
class Encoder():
    "encode a sequence of values to a file"
    
    value_max = 1 << 30 - 1
    "the max value that can be encoded.  Larger values will fail an assert"
    
    def __init__(self, coded_file, detailed_steps = 0):
        self.low = 0
        self.high = 0xffffffff
        self.underflow = 0
        self.coded_file = coded_file
        self.start_position = coded_file.tell()
        

    def output(self):
        """Output bits"""
        while True:
            # if the msb of low == msb of high
            if (self.low ^ self.high) & 0x80000000 == 0:
                bit = self.low >> 31
                write_bit(self.coded_file, bit)
                not_bit = bit ^ 1
                while self.underflow > 0:
                    write_bit(self.coded_file, not_bit)
                    self.underflow = self.underflow - 1
                        
            elif (self.low & 0xc0000000) == 0x40000000 and (self.high & 0xc0000000) == 0x80000000:
                self.underflow = self.underflow + 1
                self.low = self.low & 0x3fffffff
                self.high = self.high | 0x40000000
            
            else:
                # done outputting bits for now
                break

            # shift
            self.low = (self.low << 1) & 0xffffffff
            self.high = ((self.high << 1) | 0x01) & 0xffffffff


    def encode(self, model_value, model_low, model_high, model_extent):
        self.extent = self.high - self.low + 1
            
        # every value in the model extent must have a unique value in this extent.
        # if not, then then two model values will map to the same value, and that means
        # that the map back during decode can be to either number.  Therefore, there
        # must be at least as many values in the coder's extent as in the model's extent.
        assert(self.extent >= model_extent)
        
        # the mapping here from model space to coder space and later back (in
        # the decoder) can have problems because the result has a fractional value
        # this is lost in the conversion to int (it's tructated off).  To compensate,
        # we add a fraction large enough so that all values but 0.0 get rounded up.
        # So, symbol == pull(push(symbol)) must be true for all symbols.
        self.high = self.low + (self.extent * model_high + model_extent - 1) / model_extent - 1
        self.low = self.low + (self.extent * model_low + model_extent - 1) / model_extent
        self.output()


    def flush(self):
        bit = (self.low >> 30) & 1
        write_bit(self.coded_file, bit)
        self.underflow = self.underflow + 1
        not_bit = bit ^ 1
        while self.underflow > 0:
            write_bit(self.coded_file, not_bit)
            self.underflow = self.underflow - 1

        # the decoder will read more bits than written as it attempts to keep
        # it's value full of useful bits.  We can either provide empty bits 
        # to read, or provide a count of valid bits.  The empty bits are at 
        # most 16 - 1, which is usually similar or smaller than the size, so 
        # chose that
        for i in range(31):
            write_bit(self.coded_file, 0)

        flush_bits(self.coded_file)
        

    def length(self):
        return (self.coded_file.tell() - self.start_position) * 8


class Decoder():
    "decode a sequence of values from a file"
    
    value_max = 1 << 30 - 1
    "the max value that can be encoded.  Larger values will fail an assert"
    
    def __init__(self, coded_file, detailed_steps = 0):
        self.low = 0
        self.high = 0xffffffff
        self.underflow = 0
        self.coded_file = coded_file
        self.start_position = coded_file.tell()
        self.value = 0
        
        for i in range(32):
            self.value = (self.value << 1) | read_bit(coded_file)        

    

    def decode(self, model_low, model_high, model_total):
        if model_total == None:
            return self.value, self.high - self.low + 1
            
        extent = self.high - self.low + 1

        # the calculation must be identical to those used by the coder.
        self.high = self.low + (extent * model_high + model_total - 1) / model_total - 1
        self.low = self.low + (extent * model_low + model_total - 1) / model_total
        
        self.input()
        assert(self.low <= self.value <= self.high)

        return self.value - self.low, self.high - self.low + 1
                
                
    def input(self):
        """Input bits"""
        while True:
            # if the msb of low == msb of high
            if (self.low ^ self.high) & 0x80000000 == 0:
                pass
                        
            elif (self.low & 0xc0000000) == 0x40000000 and (self.high & 0xc0000000) == 0x80000000:
                self.value = self.value ^ 0x40000000
                self.low = self.low & 0x3fffffff
                self.high = self.high | 0x40000000
            
            else:
                # done outputting bits for now
                break

            # shift
            self.low = (self.low << 1) & 0xffffffff
            self.high = ((self.high << 1) | 0x01) & 0xffffffff
            bit = read_bit(self.coded_file)
            self.value = ((self.value << 1) | bit) & 0xffffffff


    def flush(self):
        pass


    def length(self):
        return (self.coded_file.tell() - self.start_position) * 8


assert(Decoder.value_max == Encoder.value_max)
