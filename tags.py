#!/usr/bin/python
#
#  Output all tag sets.
#

from myflickr import *

i = 0
tot = len(root["photos"])
for p in root["photos"].values():
    try:
        print p.tags
    except:
        sys.stderr.write("EXCEPTION\n")
        1
    i += 1
    sys.stderr.write("\tTag count done for %s images\n" % common.str.percent(i, tot))
