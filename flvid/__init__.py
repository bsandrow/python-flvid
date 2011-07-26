import re
from pprint   import pprint as PP

registered_scrapers = []

class Controller(object):
    def determine_scraper(self, url):
        for cls in registered_scrapers:
            scraper = cls()
            if scraper.should_scrape_url(url):
                return cls
        return None

    def get_video(self, url, scraper=None):
        if scraper is None:
            sc      = self.determine_scraper(url)
            scraper = sc()
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
        return "<%s (format_fallback_order: %s, all_formats: %s, format_urls: %s)>" \
                    % (self.__class__.__name__, self.format_fallback_order, self.all_formats, self.format_urls)

class Scraper(object):
    video_class = None

    def should_scrape_url(self, url):
        """ Determine if this processor thinks it should process this url """
        if type(self.url_pattern) == str:
            return self.url.starts_with(self.url_pattern)
        else:
            m = self.url_pattern.search(url)
            return m is not None

    def scrape_video(self, url):
        """ (Stub) Extract a direct flash video url from the passed url. """
        raise UnimplementedError('Function unimplemented')

class UnimplementedError(Exception):
    ''' Error to raise when a function is unimplemented. '''

class VideoPageParseError(Exception):
    ''' Error to parse page '''

import flvid.scrapers.youtube as youtube
youtube.register()

if __name__ == '__main__':
    f = Flvid()
    f.get_video_url('http://www.youtube.com/watch?v=nXFF5_GIsV0&feature=aso')
