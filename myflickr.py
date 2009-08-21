#
#  Flickr spider helper functions.
#

# Total number of results to find for each query
#total = 10000
total = 1000
#total = 100

# Number of search queries to return per page. No need to modify this.
queries_per_page = 500
#queries_per_page = 50

#seed_queries = ["mountain", "balloon", "car", "statue", "plane", "man", "lake", "tree", "sky", "crowd", "snow", "sunset", "wedding", "dog", "park", "architecture", "beach", "water", "house", "garden", "bird", "insect"]
seed_queries = ["mountain", "balloon", "car", "statue", "plane", "man", "lake", "tree", "sky", "crowd", "snow", "sunset", "wedding", "dog", "park", "architecture", "beach", "water", "house", "garden", "bird", "insect", "africa", "amsterdam", "animals", "architecture", "art", "australia", "baby", "band", "barcelona", "beach", "berlin", "bird", "birthday", "black", "blackandwhite", "blue", "boston", "bw", "california", "cameraphone", "camping", "canada", "canon", "car", "cat", "chicago", "china", "christmas", "church", "city", "clouds", "color", "concert", "cute", "dance", "day", "de", "dog", "england", "europe", "family", "festival", "film", "florida", "flower", "flowers", "food", "france", "friends", "fun", "garden", "geotagged", "germany", "girl", "girls", "graffiti", "green", "halloween", "hawaii", "hiking", "holiday", "home", "honeymoon", "house", "india", "ireland", "island", "italia", "italy", "japan", "july", "june", "kids", "la", "lake", "landscape", "light", "live", "london", "macro", "may", "me", "mexico", "mountain", "mountains", "museum", "music", "nature", "new", "newyork", "newyorkcity", "night", "nikon", "nyc", "ocean", "paris", "park", "party", "people", "photo", "photography", "photos", "portrait", "red", "river", "rock", "rome", "san", "sanfrancisco", "scotland", "sea", "seattle", "show", "sky", "sunset", "taiwan", "texas", "thailand", "tokyo", "toronto", "tour", "travel", "tree", "trees", "trip", "uk", "urban", "usa", "vacation", "vancouver", "washington", "water", "wedding", "white", "winter", "yellow", "york", "zoo"]


# Ignore these queries
blacklist_queries = [ 'abigfave', 'bravo', 'aplusphoto', 'diamondclassphotographer', 'anawesomeshot', 'hdr', 'impressedbeauty', 'supershot', 'nikon', 'flickrdiamond', 'superbmasterpiece', 'canon', 'superaplus', 'blueribbonwinner', 'soe', 'macro', 'searchthebest', 'topf25', 'interestingness', 'outstandingshots', 'flickrsbest', 'platinumphoto', 'theperfectphotographer', 'photomatix', 'goldenphotographer', 'quality', 'theunforgettablepictures', 'i500', 'wow', 'superhearts', 'goldstaraward' ]
#blacklist_queries = [ ]

import flickrapi
import keys
api_key = keys.api_key
api_secret = keys.api_secret
#flickr = flickrapi.FlickrAPI(api_key, format='etree')
flickr = flickrapi.FlickrAPI(api_key, api_secret, format='etree')

import sys
import common.str
from collections import defaultdict

import ZODB.config
import transaction
from BTrees.OOBTree import OOBTree
db = ZODB.config.databaseFromURL('flickr.conf')
conn = db.open()
root = conn.root()
if not root.has_key('finished_queries'):
    root['finished_queries'] = OOBTree()
if not root.has_key('search_page'):
    root['search_page'] = OOBTree()
if not root.has_key('photos'):
    root['photos'] = OOBTree()
# Commit the change
transaction.commit()

from persistent import Persistent
class Photo(Persistent):
    """
    Photo information.
    """
    def __init__(self, dict):
        """
        Initialize a photo, using the value in dict.
        @note: This should not be called directly, because caching may get messed up.
        Instead, use photo_from_*().
        """
        self.update(dict)

    def update(self, dict):
        """
        Update the photo according to this dict.
        """
        self.__dict__.update(dict)
        self._p_changed = True

    url_small_square = property(fget = lambda self: "http://farm%s.static.flickr.com/%s/%s_%s_s.jpg" % (self.farm, self.server, self.id, self.secret), \
        doc="URL for 75x75 small square thumbnail.")

    def _get_info(self):
        """
        Get the specific information for this image.
        @note: Some information in here may be redundant, e.g. the ID may be stored in here as well as the class attribute.
        """
        if "_info" not in self.__dict__:
            sys.stderr.write("\tAbout to call flickr.photos_getInfo(photo_id=%s, secret=%s)...\n" % (self.id, self.secret))
            self._info = flickr.photos_getInfo(photo_id = self.id, secret = self.secret)
            self._p_changed = True
            sys.stderr.write("\t...done calling flickr.photos_getInfo(photo_id=%s, secret=%s)\n" % (self.id, self.secret))
        return self._info

    def _get_photoinfo(self):
        return self.info.find('photo')

    info = property(fget = _get_info, doc="Get the specific information for this image.")
    photoinfo = property(fget = _get_photoinfo, doc="Get the specific photo information for this image.")

    def _get_tags(self):
        """
        Return a list of the "clean" tags.
        @note: Clean tags are 'as processed by Flickr.' Does not contain
        punctuation or spaces. We could also retrieve the raw tags,
        as entered by the user.
        """
        return [t.text for t in self.photoinfo.find("tags").findall("tag")]
    tags = property(fget = _get_tags)

def photo_from_id(id):
    """
    Return the photo with a particular ID.
    """
    return root['photos'][id]

def photo_from_infodict(dict):
    """
    Return the photo corresponding to a dictionary of information.
    We retrieve the photo by ID.
    """
    id = dict['id']
    if id not in root['photos']:
        root['photos'][id] = Photo(dict)
    #We also update the entries of the photo according to the dictionary.
#    else:
#        root['photos'][id].update(dict)
    return root['photos'][id]

def search_page(query, queries_per_page, page, sort="relevance"):
    """
    Retrieve a specific search page.
    @note: These searches are cached.
    """
    dict = {'query': query, 'queries_per_page': queries_per_page, 'page': page, 'sort': sort}
    if dict not in root['search_page']:
        sys.stderr.write("\tAbout to call flickr.photos_search(per_page=%s, tags=%s, sort=%s, page=%s)...\n" % (queries_per_page, query, sort, page))
        root['search_page'][dict] = flickr.photos_search(per_page=queries_per_page, tags=query, sort=sort, page=page)
        #= flickr.photos_search(per_page=queries_per_page, text=query, sort="relevance", page=page)
        transaction.commit()
        sys.stderr.write("\t...done calling flickr.photos_search(per_page=%s, tags=%s, sort='relevance', page=%s)\n" % (queries_per_page, query, page))
    return root['search_page'][dict]

def search(query, total=total, queries_per_page=queries_per_page):
    """
    Search for many images with a particular tag.
    Return a set of photo IDs, ordered by relevancy.
    """
    results = []
    for page in range(1, 1 + int(total/queries_per_page)):
        result = search_page(query, queries_per_page, page)
        for set in result.findall('photos'):
            for p in set.findall('photo'):
                p = photo_from_infodict(p.attrib)
                results.append(p.id)
#                print photo_from_id(results[-1]).url_small_square
        sys.stderr.write("\tResults has %s done\n" % common.str.percent(len(results), total))
        transaction.commit()
    return results

def query(query):
    dict = {'query': query, 'total': total}
    if dict not in root['finished_queries']:
        sys.stderr.write("BEGIN QUERY %s...\n" % query)
        for id in search(query):
            p = photo_from_id(id)
        sys.stderr.write("...END QUERY %s\n" % query)
        root['finished_queries'][dict] = True
        transaction.commit()
    else:
        sys.stderr.write("ALREADY HAVE QUERY %s\n" % query)

def sort_tags(length=500):
    """
    Return a list of pairs, sorted from strongest to weakest.
    Each pair is (score, tag)
    @param length: The length of the list to return
    """
    score = defaultdict(float)
    i = 0
    tot = len(root["photos"])
    for p in root["photos"].values():
        try:
            tags = p.tags
            for t in tags:
                if t in blacklist_queries: continue
                score[t] += 1. / len(tags)
        except:
            sys.stderr.write("EXCEPTION\n")
            pass
        i += 1
        sys.stderr.write("\tTag count done for %s images\n" % common.str.percent(i, tot))
        if i % 100 == 0: transaction.commit()
    transaction.commit()
    pairs = [(score[t], t) for t in score]
    pairs.sort()
    pairs.reverse()
    return pairs[:length]
