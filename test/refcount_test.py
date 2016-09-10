import numpy as np
import sys

import libnumbuf

value = 1
print "TRUE REF COUNT aaa = {}".format(sys.getrefcount(False))
schema, size, serialized = libnumbuf.serialize_list([value])
print "TRUE REF COUNT bbb = {}".format(sys.getrefcount(False))
size = size + 8 + len(schema) + 4096 * 4
print "TRUE REF COUNT ccc = {}".format(sys.getrefcount(False))
buff = np.zeros(size)
#buff, segmentid = raylib.allocate_buffer(self.handle, objectid, size)
print "TRUE REF COUNT ddd = {}".format(sys.getrefcount(False))
np.frombuffer(buff, dtype="int64", count=1)[0] = len(schema)
print "TRUE REF COUNT eee = {}".format(sys.getrefcount(False))
metadata = np.frombuffer(buff, dtype="byte", offset=8, count=len(schema))
print "TRUE REF COUNT fff = {}".format(sys.getrefcount(False))
metadata[:] = schema
print "TRUE REF COUNT ggg = {}".format(sys.getrefcount(False))
