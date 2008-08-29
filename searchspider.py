#!/usr/bin/python
#
#  Spider flickr information, starting from the seed queries.
#   For a query, get the 10K most relevant tag search results.
#   Saves the image information for each of these images.
#   Find the next query by the most common tag.
#  Information is cached, so that we hit the flickr server as little as possible.
#

from myflickr import *

for seed_query in seed_queries:
    query(seed_query)

while 1:
    sorted = sort_tags()
    sys.stderr.write("Sorted tags:\n")
    for p in sorted:
        sys.stderr.write("\t%s\n" % `p`)
    for (score, tag) in sorted:
        dict = {'query': tag, 'total': total}
        if dict not in root['finished_queries']:
            try:
                query(tag)
                break
            except:
                sys.stderr.write("EXCEPTION\n")
                1
