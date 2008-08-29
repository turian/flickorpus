flickorpus
==========

flickorpus collects an image and tag corpus from flickr.
For different tag queries, it finds the N most relevant images, and retrieves
the tags for those images.
It never actually downloads images themselves, it merely has sufficient
metadata to concoct the correct URL.

Written by Joseph Turian
    <lastname at iro dot umontreal dot ca>

Available at:
    http://www.pylearn.org/flickorpus/

LICENSE
-------
MIT license. See LICENSE.txt

If you collect good data with this program, we encourage you to pay
it forward and share with others.


REQUIREMENTS
------------

* Python

* Beej's Python Flickr API: http://flickrapi.sourceforge.net/

* ZODB: http://wiki.zope.org/ZODB/FrontPage


GETTING STARTED
---------------

* Get the source code:
    hg clone http://pylearn.org/hg/flickorpus

* Copy keys.py.tmpl to keys.py, and enter your flickr API keys.

* ZODB:
    * Install ZODB: http://wiki.zope.org/ZODB/FrontPage
    * Get a ZODB server running, e.g. ./zeo.sh

* Try running ./searchspider.py


SOME DETAILS
------------

ZODB gives the program persistent state, so you can start and stop
execution as you please. Work will continue where you left off.

Flickr API queries are cached in ZODB. Note that search results may get
stale over time.

Flickr typically throttles you to two requests per second.

It wouldn't be too hard to extend this program to operate concurrently.
I have not done so, though. Email me for more details.

./searchspider.py
    The search spider begins with the seed queries in myflickr.seed_queries.

    For each query, it searches for the 1000 (= myflickr.total) most relevant
    results with this tag. This requires 2 = 1000/500 (= myflickr.total /
    myflickr.queries_per_page) API requests.
    For each of the 1000 results, it retrieves their metadata. In particular,
    it retrieves every tag for the image. If an image ID was returned previously
    in another query, then its metadata is already cached and does not need to
    be retrieved. Otherwise, an API request is issued.

    After all seed queries have been pulled, the spider goes over the entire
    database of stored image metadata. It determines the most common tag that
    has not already been queried and that is not present in
    myflickr.blacklist_queries. It then queries this tag.

    Lather, rinse repeat.

./getresults.py tag
    Search for the 1000 (= myflickr.total) most relevant results with
    this tag, and output the 75x75 images in HTML.

./tags.py
    For every image in the ZODB, retrieve its tags and output them.

COMMENTS, QUESTIONS, ETC.
-------------------------

Please email the author.
