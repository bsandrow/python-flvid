import re

registered_scrapers = []
registered_formats = {
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
    format_fallback_order = None
    all_formats           = None
    format_urls           = None

    @property
    def available_formats(self):
        return self.format_urls.keys()

    def default_format(self):
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
