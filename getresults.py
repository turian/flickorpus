#!/usr/bin/python
#
#  Get the most relevant search results for the query in sys.argv[1]
#

from myflickr import *

for id in search(sys.argv[1]):
    p = photo_from_id(id)
    print "<img src='%s'>" % p.url_small_square
