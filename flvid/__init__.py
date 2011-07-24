import httplib2
import json
import re
import lxml.html
from urllib   import unquote
from StringIO import StringIO
from pprint   import pprint as PP

registered_scrapers = []

class Flvid(object):
    def determine_scraper(self, url):
        for cls in registered_scrapers:
            scraper = cls()
            if scraper.should_scrape_url(url):
                return (cls.__name__, cls)
        return ('', None)

    def get_video_url(self, url, scraper=None, format=None):
        if scraper is None:
            sc = self.determine_scraper(url)
            scraper = sc[1]()
        return scraper.scrape_video(url, format)

class Video(object):
    pass

class Scraper(object):
    def should_scrape_url(self, url):
        """ Determine if this processor thinks it should process this url """
        if type(self.url_re) == str:
            return self.url.starts_with(self.url_re)
        else:
            m = self.url_re.search(url)
            return m is not None

    def process(self, url):
        """ (Stub) Extract a direct flash video url from the passed url. """
        raise UnimplementedError('Function unimplemented')

class YouTube(Scraper):
    fmt_order = [
        '44', '35',         # prefer 'large' size
        '43', '18', '34',   # second 'medium' size
        '22', '45',         # third 720p
        '37',               # fourth 1080p
        '5'                 # lastly 'small'
    ]

    formats = {
        '43': { 'type': 'video/webm', 'quality': 'medium','size': '640x480' },
        '44': { 'type': 'video/webm', 'quality': 'large', 'size': '854x480' },
        '45': { 'type': 'video/webm', 'quality': 'hd720', 'size': '1280x720'},
        '18': { 'type': 'video/mp4',  'quality': 'medium','size': '640x360' },
        '22': { 'type': 'video/mp4',  'quality': 'hd720', 'size': '1280x720'},
        '37': { 'type': 'video/mp4',  'quality': 'hd1080','size': '1920x1080'},
        '34': { 'type': 'video/x-flv','quality': 'medium','size': '640x360' },
        '35': { 'type': 'video/x-flv','quality': 'large', 'size': '854x480' },
        '5':  { 'type': 'video/x-flv','quality': 'small', 'size': '320x240' },
    }

    url_re = re.compile(r'^https?://(?:www\.)?youtube\.com/watch')

    def _fmt_to_url_map(self, info):
        fmt_to_url = {}
        fmt_stream_map = info['args']['fmt_stream_map'].split(',')
        for stream in fmt_stream_map:
            stream_parts = stream.split('|')
            fmt_to_url[stream_parts[0]] = stream_parts[1]
        return fmt_to_url

    def _extract_fmt_stream_map(self, d):
        ''' Cruft leftover for possible debugging purposes '''
        fmt_stream_map = {}
        for x in [ x.split('|') for x in d['args']['fmt_stream_map'].split(',') ]:
            fmt_stream_map[x[0]] = { 'video_url': x[1], 'fallback': x[3], }
        return fmt_stream_map

    def _extract_fmt_list(self, d):
        ''' Cruft leftover for possible debugging purposes '''
        return [ x.split('/') for x in d['args']['fmt_list'].split(',') ]

    def _available_formats(self, info):
        return [ fmt.split('/')[0] for fmt in info['args']['fmt_list'].split(',') ]

    def _get_default_format(self, d):
        availkeys = [ x[0] for x in self._available_formats(d) ]
        for fmtkey in self.fmt_order:
            if fmtkey in availkeys:
                return fmtkey
        raise Exception()

    def extract_info(self, url):
        h = httplib2.Http()
        resp, content = h.request(url, 'GET')
        tree = lxml.html.fromstring(content)
        r = tree.xpath('/html/body/script[4]')
        m = re.search(r'var swfConfig = (\{".*"\});', lxml.html.tostring(r[0]))
        if m is None:
            raise VideoPageParseError("Could not extract direct link")
        swfconf = json.loads(m.group(1))
        return {
            'avail_fmts' : self._available_formats(swfconf),
            'fmt_urls'   : self._fmt_to_url_map(swfconf),
            'default_fmt': self._get_default_format(swfconf),
        }

    def scrape_video(self, url, format):
        info = self.extract_info(url)
        if format is None:
            format = info['default_fmt']
        return info['fmt_urls'][format]

registered_scrapers.append(YouTube)

class UnimplementedError(Exception):
    ''' Error to raise when a function is unimplemented. '''

class VideoPageParseError(Exception):
    ''' Error to parse page '''

if __name__ == '__main__':
    f = Flvid()
    f.get_video_url('http://www.youtube.com/watch?v=nXFF5_GIsV0&feature=aso')
