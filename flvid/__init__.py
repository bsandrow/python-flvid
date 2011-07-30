import re
import urllib
import os

registered_scrapers = []
registered_types = {
    'flv':  { 'mimetype': 'video/x-flv', 'extension':'flv'  },
    'mp4':  { 'mimetype': 'video/mp4',   'extension':'mp4'  },
    'webm': { 'mimetype': 'video/webm',  'extension':'webm' },
}

def determine_scraper(url):
    ''' Match the url against the list of registered scrapers and return
    the class of the first matching scraper '''
    for cls in registered_scrapers:
        scraper = cls()
        if scraper.should_scrape_url(url):
            return cls
    return None

def get_video(url, scraper=None):
    ''' Return a Video object containing all of the scraped metadata for
    a video. The scraper can be specified, otherwise determine_scraper() will
    be used to determine the scraper to use. '''
    if scraper is None:
        scraper_class   = determine_scraper(url)
        scraper         = scraper_class()
    return scraper.scrape_video(url)

class Video(object):
    ''' A representation of the video that is encompassed by a video page that
    is being parsed. This allows easy storage of relevant metadata out of the
    parser, and allows a separation between the acts of parsing the metadata
    from the page and performing actions on that metadata. '''

    title                 = None
    format_fallback_order = None
    all_formats           = None
    format_urls           = None

    @property
    def available_formats(self):
        return self.format_urls.keys()

    @property
    def default_format(self):
        ''' Return the default format key. Runs through
        self.format_fallback_order in order, and returns the first key it finds
        in self.available_formats. Returns None if there is no intersection
        between self.available_formats and self.format_fallback_order.
        '''
        for format in self.format_fallback_order:
            if format in self.available_formats:
                return format
        return None

    def __str__(self):
        ffo = 'format_fallback_order: %s' % self.format_fallback_order
        cls = self.__class__.__name__
        afs = 'all_formats: %s' % self.all_formats
        fus = 'format_urls: %s' % self.format_urls
        return "<%s (%s, %s, %s)>" % (cls, ffo, afs, fus)

    def dest_filebase(self):
        ''' This is a small abstraction to allow sub-classes to easily change
        the base of the filename from the default of self.title without needing
        to re-implement all of the functionality in Video.build_dest() '''
        return self.title

    def build_dest(self, dest=None, format=None):
        ''' Return the path to the file we want to download the video to. Uses
        the default format if no format is passed in. Uses the default file
        basename + the current directory if dest is None. Otherwise, it just
        passes dest back out. '''
        if format is None:
            extension = registered_types[self.all_formats[self.default_format]['type']]['extension']
        else:
            extension = registered_types[self.all_formats[format]['type']]['extension']

        if dest is None:
            dir  = os.getcwd()
            file = '%s.%s' % (self.dest_filebase(), extension)
        elif os.path.isdir(dest):
            dir  = dest
            file = '%s.%s' % (self.dest_filebase(), extension)
        else:
            return dest

        return os.path.join(dir, file)

    def download_video(self, format=None, dest=None):
        ''' Download the video that an instance of this class (or sub-class)
        represents. Attaching this functionality to the Video() class allows
        sub-classes to do whatever funkiness is needed (such as constructing
        weird http requests) internally, rather than requiring the user of this
        class to understand and implement that functionality. '''
        destination = self.build_dest(dest, format)
        url         = self.format_urls[format if format is not None else self.default_format]
        return urllib.urlretrieve(url, destination)

class Scraper(object):
    ''' A base object for video page scrapers. At least initially, this base
    class is mostly here to help form some sort of structure, and to add the
    minimal amount of drop-in functionality that is
    Scraper.should_scrape_url() '''

    # Sub-classes should set this to whatever video class they use.
    video_class = None

    def should_scrape_url(self, url):
        ''' Return True/False based on whether or not this scraper is able
        process the url. This is a generic version that should work in most
        cases, but there are definitely cases where you will want to overload
        this (e.g. breaking apart the query string into params to make sure
        that certain params exist).'''
        if type(self.url_pattern) == str:
            return self.url.starts_with(self.url_pattern)
        else:
            m = self.url_pattern.search(url)
            return m is not None

    def scrape_video(self, url):
        ''' A stub for the main functionality of a Scraper class. This is meant
        to return an object of class self.video_class (which should be a
        sub-class of Video).'''
        raise UnimplementedError('Function unimplemented')

class UnimplementedError(Exception):
    ''' Error to raise when a function is unimplemented. '''

class VideoPageParseError(Exception):
    ''' Error to parse page '''

for m in ['youtube']:
    module = __import__('flvid.scrapers.%s' % m, fromlist=[m])
    module.register()
