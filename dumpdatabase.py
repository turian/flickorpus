#!/usr/bin/python
#
#  Dump photos in the database to JSON stdout.
#

from myflickr import *

import common.xml2json.parker
import common.json
import common.myyaml
import copy

photos = []
for p in root["photos"]:
    # You have to load the info first, or it will not be properly cached in the database
    info = common.xml2json.parker.convert(root["photos"][p].info)
#    print p
    photo = copy.copy(root["photos"][p].__dict__)
    del photo["_info"]
    info = info["photo"]
    photo["info"] = info
    photos.append(photo)

common.json.dump(photos, sys.stdout, indent=4)
