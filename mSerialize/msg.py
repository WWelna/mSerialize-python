# Copyright (C) 2025 William Welna (wwelna@occultusterra.com)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following condition.

# * The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.

# In addition, the following restrictions apply:

# * The software, either in source or compiled binary form, with or without any
#   modification, may not be used with or incorporated into any other software
#   that used an Artificial Intelligence (AI) model and/or Large Language Model
#   (LLM) to generate any portion of that other software's source code, binaries,
#   or artwork.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from io import BytesIO
import struct
import time

## Def ##
MSG_TRUE   = 0b01000001
MSG_FALSE  = 0b00100001
MSG_NIL    = 0b01100001
MSG_UBYTE  = 0b00000001
MSG_SBYTE  = 0b00000010
MSG_USHORT = 0b00000011
MSG_SSHORT = 0b00000100
MSG_UINT   = 0b00000101
MSG_SINT   = 0b00000110
MSG_ULONG  = 0b00000111
MSG_SLONG  = 0b00001000
MSG_FLOAT  = 0b00001001
MSG_DOUBLE = 0b00001010

MSG_TIME   = 0b00100111

MSG_CSTRING  = 0b00001100

# Not Implimented
MSG_CSTRINGC8  = 0b10101100
MSG_CSTRINGC16 = 0b11001100
MSG_CSTRINGC32 = 0b11101100
# Not Implimented

MSG_RAW    = 0b00001001
MSG_RAW8   = 0b00101001
MSG_RAW16  = 0b01001001
MSG_RAW32  = 0b01101001
MSG_RAWUN  = 0b10001001

# Not Implimented
MSG_RAWC8  = 0b10101001
MSG_RAWC16 = 0b11001001
MSG_RAWC32 = 0b11101001
# Not Implimented

MSG_UTF8   = 0b00001101
MSG_UTF8_8 = 0b00101101
MSG_UTF8_16= 0b01001101
MSG_UTF8_32= 0b01101101
MSG_UTF8_UN= 0b10001101

# Not Implimented
MSG_UTF8C_8  = 0b10101101
MSG_UTF8C_16 = 0b11001101
MSG_UTF8C_32 = 0b11101101
# Not Implimented

MSG_1D     = 0b00001110
MSG_1D8    = 0b00101110
MSG_1D16   = 0b01001110
MSG_1D32   = 0b01101110
MSG_1DUN   = 0b10001110

MSG_MAP    = 0b00001111
MSG_MAP8   = 0b00101111
MSG_MAP16  = 0b01001111
MSG_MAP32  = 0b01101111
MSG_MAPUN  = 0b10001111
## Def ##

## Wrapper For Binary Data ##
class BinData(bytes): pass
## Wrapper For Binary Data ##

## Exception Classes ##
class OutOfData(Exception):
    def __init__(self, previous=None, next=None, message=None):
        self.previous = previous
        self.next = next
        self.message = message
## Exception Classes ##

def pack(b):
    p = Packer()
    p.add(b)
    return p.finish()

## Packer Class ##
class Packer:

    def __init__(self):
        self.buffer = BytesIO()
    
    def __enter__(self):
        pass

    def __exit__(self):
        self.buffer.close()
    
    def add(self, t):
        if isinstance(t, BinData):
            self.msgw_raw(t)
            return
        kind = type(t).__name__
        if kind == 'int' and int.bit_length(t) <= 64:
            if int.bit_length(t) <= 8 and t >= 0:
                self.msgw_ubyte(t)
            elif int.bit_length(t) <= 8 and t < 0:
                self.msgw_sbyte(t)
            elif int.bit_length(t) <= 16 and t >= 0:
                self.msgw_ushort(t)
            elif int.bit_length(t) <= 16 and t < 0:
                self.msgw_sshort(t)
            elif int.bit_length(t) <= 32 and t >= 0:
                self.msgw_uint(t)
            elif int.bit_length(t) <= 32 and t < 0:
                self.msgw_sint(t)
            elif int.bit_length(t) <= 64 and t >= 0:
                self.msgw_ulong(t)
            elif int.bit_length(t) <= 64 and t < 0:
                self.msgw_slong(t)
            else: raise TypeError('Insane bit_length() detected for int')
        elif kind == 'float':
            self.msgw_double(t)
        elif kind == 'str':
            if t.isascii == True:
                self.msgw_cstring(t)
            else:
                self.msgw_utf8(t.encode('utf-8'))
        elif kind == 'bytearray':
            self.msgw_raw(str(t))
        elif kind == 'bool':
            if t:
                self.msgw_true()
            else:
                self.msgw_false()
        elif kind == 'NoneType':
            self.msgw_nil()
        elif kind == 'datetime':
            self.msgw_time(long(time.mktime(t.timetuple())))
        elif kind == 'tuple' or kind == 'list':
            self.msgw_1d(t)
        elif kind == 'dict':
            self.msgw_map(t)
        else: raise TypeError('Not Supported-> '+kind)
    
    ## Bytes ##
    def msgw_true(self):
        self.buffer.write(struct.pack('>B', MSG_TRUE))
    def msgw_false(self):
        self.buffer.write(struct.pack('>B', MSG_FALSE))
    def msgw_nil(self):
        self.buffer.write(struct.pack('>B', MSG_NIL))
    def msgw_ubyte(self, b):
        self.buffer.write(struct.pack('>BB', MSG_UBYTE, b))
    def msgw_sbyte(self, b):
        self.buffer.write(struct.pack('>Bb', MSG_SBYTE, b))
    ## Bytes ##
    ## Shorts ##
    def msgw_ushort(self, s):
        self.buffer.write(struct.pack('>BH', MSG_USHORT, s))
    def msgw_sshort(self, s):
        self.buffer.write(struct.pack('>Bh', MSG_SSHORT, s))
    ## Shorts ##
    ## Integers ##
    def msgw_uint(self, i):
        self.buffer.write(struct.pack('>BI', MSG_UINT, i))
    def msgw_sint(self, i):
        self.buffer.write(struct.pack('>Bi', MSG_SINT, i))
    ## Integers ##
    ## Longs ##
    def msgw_ulong(self, l):
        self.buffer.write(struct.pack('>BQ', MSG_ULONG, l))
    def msgw_time(self, l):
        self.buffer.write(struct.pack('>BQ', MSG_TIME, l))
    def msgw_slong(self, l):
        self.buffer.write(struct.pack('>Bq', MSG_SLONG, l))
    ## Longs ##
    ## Floats N Doubles ##
    def msgw_float(self, ff):
        self.buffer.write(struct.pack('>Bf', MSG_FLOAT, ff))
    def msgw_double(self, d):
        self.buffer.write(struct.pack('>Bd', MSG_DOUBLE, d))
    ## Floats N Doubles ##
    ## Data Strings ##
    def msgw_raw(self, r):
        if int.bit_length(len(r)) <= 8:
            self.msgw_raw8(r)
        elif int.bit_length(len(r)) <= 16:
            self.msgw_raw16(r)
        elif int.bit_length(len(r)) <= 32:
            self.msgw_raw32(r)
        else: pass
    def msgw_raw8(self, r):
        self.buffer.write(struct.pack('>BB'+str(len(r))+'s', MSG_RAW8, len(r), r))
    def msgw_raw16(self, r):
        self.buffer.write(struct.pack('>BH'+str(len(r))+'s', MSG_RAW16, len(r), r))
    def msgw_raw32(self, r):
        self.buffer.write(struct.pack('>BI'+str(len(r))+'s', MSG_RAW32, len(r), r))
    def msgw_utf8(self, r):
        try:
            if type(r).__name__ == 'str':
                r = r.encode('utf-8')
            if int.bit_length(len(r)) <= 8:
                self.msgw_utf8_8(r)
            elif int.bit_length(len(r)) <= 16:
                self.msgw_utf8_16(r)
            elif int.bit_length(len(r)) <= 32:
                self.msgw_utf8_32(r)
            else: raise TypeError('Insane UTF8 Length')
        except UnicodeDecodeError:
            self.msgw_raw(r)
    def msgw_utf8_8(self, r):
        self.buffer.write(struct.pack('>BB'+str(len(r))+'s', MSG_UTF8_8, len(r), r))
    def msgw_utf8_16(self, r):
        self.buffer.write(struct.pack('>BH'+str(len(r))+'s', MSG_UTF8_16, len(r), r))
    def msgw_utf8_32(self, r):
        self.buffer.write(struct.pack('>BI'+str(len(r))+'s', MSG_UTF8_32, len(r), r))
    def msgw_cstring(self, s):
        self.buffer.write(struct.pack('>B'+str(len(s))+'sx', MSG_CSTRING, s.encode('utf-8')))
    ## Data Strings ##
    ## Maps and Arrays ##
    def msgw_1d(self, r):
        entries = len(r)
        if int.bit_length(entries) <= 8:
            self.buffer.write(struct.pack('>BB', MSG_1D8, entries))
        elif int.bit_length(entries) <= 16:
            self.buffer.write(struct.pack('>BH', MSG_1D16, entries))
        elif int.bit_length(entries) <= 32:
            self.buffer.write(struct.pack('>BI', MSG_1D32, entries))
        for x in r:
            self.add(x)
    def msgw_map(self, r):
        entries = len(r)
        if int.bit_length(entries) <= 8:
            self.buffer.write(struct.pack('>BB', MSG_MAP8, entries))
        elif int.bit_length(entries) <= 16:
            self.buffer.write(struct.pack('>BH', MSG_MAP16, entries))
        elif int.bit_length(entries) <= 32:
            self.buffer.write(struct.pack('>BI', MSG_MAP32, entries))
        for k,v in r.items():
            self.add(k)
            self.add(v)
    ## Maps and Arrays ##

    def size(self):
        return len(self.buffer.getvalue())

    def finish(self):
        ret = self.buffer.getvalue()
        self.buffer.close()
        return ret
## Packer Class ##

def unpack_gen(b):
    p = Unpacker(b)
    try:
        yield p.decode()
    except OutOfData:
        p.finish()

def unpack(b):
    ret = []
    for e in unpack_gen(b):
        ret.append(e)
    return tuple(ret)

## Unpacker Class ##
class Unpacker:

    def __init__(self, b):
        self.subtype_mask = 0b11100000
        self.type_mask = 0b00011111
        self.buffer = BytesIO(b)
    
    def __enter__(self):
        pass

    def __exit__(self):
        self.finish()

    def decode(self):
        
        if len(self.buffer.read(1)) == 0:
            raise OutOfData
        else: self.buffer.seek(self.buffer.tell()-1)

        header = struct.unpack_from('>B', self.buffer.read(1))[0]
        header_type = header & self.type_mask
        header_subtype = header & self.subtype_mask
        if header_type == MSG_RAW:
            if header == MSG_RAW8:
                length = struct.unpack_from('>B', self.buffer.read(1))[0]
                return BinData(self.buffer.read(length))
            elif header == MSG_RAW16:
                length = struct.unpack_from('>H', self.buffer.read(2))[0]
                return BinData(self.buffer.read(length))
            elif header == MSG_RAW32:
                length = struct.unpack_from('>I', self.buffer.read(4))[0]
                return BinData(self.buffer.read(length))
            else: pass
        if header_type == MSG_UTF8:
            if header == MSG_UTF8_8:
                length = struct.unpack_from('>B', self.buffer.read(1))[0]
                return str(self.buffer.read(length), encoding='utf-8')
            elif header == MSG_UTF8_16:
                length = struct.unpack_from('>H', self.buffer.read(2))[0]
                return str(self.buffer.read(length), encoding='utf-8')
            elif header == MSG_UTF8_32:
                length = struct.unpack_from('>I', self.buffer.read(4))[0]
                return str(self.buffer.read(length), encoding='utf-8')
        if header_type == MSG_1D:
            if header == MSG_1D8:
                entries = struct.unpack_from('>B', self.buffer.read(1))[0]
                ret = []
                while entries > 0:
                    ret.append(self.decode())
                    entries -= 1
                return ret
            elif header == MSG_1D16:
                entries = struct.unpack_from('>H', self.buffer.read(2))[0]
                ret = []
                while entries > 0:
                    ret.append(self.decode())
                    entries -= 1
                return ret
            elif header == MSG_1D32:
                entries = struct.unpack_from('>I', self.buffer.read(4))[0]
                ret = []
                while entries > 0:
                    ret.append(self.decode())
                    entries -= 1
                return ret
            else: pass
        if header_type == MSG_MAP:
            if header == MSG_MAP8:
                entries = struct.unpack_from('>B', self.buffer.read(1))[0]
                ret = {}
                while entries > 0:
                    t1 = self.decode()
                    t2 = self.decode()
                    ret[t1] = t2
                    entries -= 1
                return ret
            elif header == MSG_MAP16:
                entries = struct.unpack_from('>H', self.buffer.read(2))[0]
                ret = {}
                while entries > 0:
                    t1 = self.decode()
                    t2 = self.decode()
                    ret[t1] = t2
                    entries -= 1
                return ret
            elif header == MSG_MAP32:
                entries = struct.unpack_from('>I', self.buffer.read(4))[0]
                ret = {}
                while entries > 0:
                    t1 = self.decode()
                    t2 = self.decode()
                    ret[t1] = t2
                    entries -= 1
                return ret
            else: pass
        if header == MSG_CSTRING:
            r = ''
            while self.buffer.read(1) != '':
                self.buffer.seek(self.buffer.tell()-1)
                c = self.buffer.read(1)
                if ord(c) == 0x00: break
                else: r += c.decode('ascii')
            return r
        if header_type == MSG_UBYTE:
            if header_subtype != 0:
                if header == MSG_TRUE: return True
                if header == MSG_FALSE: return False
                if header == MSG_NIL: return None
            else: return struct.unpack_from('>B', self.buffer.read(1))[0]
        elif header_type == MSG_SBYTE:
            return struct.unpack_from('>b', self.buffer.read(1))[0]
        elif header_type == MSG_USHORT:
            return struct.unpack_from('>H', self.buffer.read(2))[0]
        elif header_type == MSG_SSHORT:
            return struct.unpack_from('>h', self.buffer.read(2))[0]
        elif header_type == MSG_UINT:
            return struct.unpack_from('>I', self.buffer.read(4))[0]
        elif header_type == MSG_SINT:
            return struct.unpack_from('>i', self.buffer.read(4))[0]
        elif header_type == MSG_ULONG:
            return struct.unpack_from('>Q', self.buffer.read(8))[0]
        elif header_type == MSG_SLONG:
            return struct.unpack_from('>q', self.buffer.read(8))[0]
        elif header_type == MSG_FLOAT:
            return struct.unpack_from('>f', self.buffer.read(4))[0]
        elif header_type == MSG_DOUBLE:
            return struct.unpack_from('>d', self.buffer.read(8))[0]
        else: raise IOError('Got Unidentifiable Type '+str(header_type)+'at '+str(self.buffer.tell()))
    
    def finish(self):
        self.buffer.close()
## Unpacker Class ##
