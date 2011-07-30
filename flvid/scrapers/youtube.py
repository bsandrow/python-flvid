import re
import flvid
import httplib2
import json
import lxml.html
from urllib import unquote

class YouTubeVideo(flvid.Video):
    format_fallback_order = [
        '44', '35',         # prefer 'large' size
        '43', '18', '34',   # second 'medium' size
        '22', '45',         # third 720p
        '37',               # fourth 1080p
        '5'                 # lastly 'small'
    ]

    all_formats = {
        '43': { 'type': 'webm', 'quality': 'medium', 'size': '640x480',   },
        '44': { 'type': 'webm', 'quality': 'large',  'size': '854x480',   },
        '45': { 'type': 'webm', 'quality': 'hd720',  'size': '1280x720',  },
        '18': { 'type': 'mp4',  'quality': 'medium', 'size': '640x360',   },
        '22': { 'type': 'mp4',  'quality': 'hd720',  'size': '1280x720',  },
        '37': { 'type': 'mp4',  'quality': 'hd1080', 'size': '1920x1080', },
        '34': { 'type': 'flv',  'quality': 'medium', 'size': '640x360',   },
        '35': { 'type': 'flv',  'quality': 'large',  'size': '854x480',   },
        '5':  { 'type': 'flv',  'quality': 'small',  'size': '320x240',   },
    }

    @classmethod
    def format_strings(cls):
        retval = []
        for k,v in cls.all_formats.iteritems():
            retval.append('%s: %s // %s // %s' % (k, v['quality'], v['size'], v['type']))
        return retval

class YouTubeVideoScraper(flvid.Scraper):
    video_class = YouTubeVideo
    url_pattern = re.compile(r'^https?://(?:www\.)?youtube\.com/watch')

    def _fmt_to_url_map(self, info):
        fmt_to_url = {}
        fmt_stream_map = info['args']['fmt_url_map'].split(',')
        for stream in fmt_stream_map:
            stream_parts = stream.split('|')
            fmt_to_url[stream_parts[0]] = stream_parts[1]
        return fmt_to_url

    def _try_embed_element(self, tree):
        r = tree.xpath('//embed')
        if len(r) != 1:
            return None

        flashvars = unquote(r[0].get('flashvars'))
        fvars = {}
        for x in flashvars.split('&'):
            y = x.split('=', 1)
            fvars[y[0]] = y[1]

        video = self.video_class()
        video.video_id = fvars['video_id']
        video.format_urls = {}

        for url in fvars['fmt_url_map'].split(','):
            parts = url.split('|')
            video.format_urls[parts[0]] = parts[1]

        return video

    def _try_script_elements(self, tree):
            patterns = [
                re.compile(r'''yt\.setConfig\(\{\s*'PLAYER_CONFIG':\s*(\{".*"\})\s*\}\);''', re.M | re.S),
                re.compile(r'var swfConfig = (\{".*"\});', re.M | re.S),
            ]

            r = tree.xpath('/html/body/script[4]')
            if len(r) < 1:
                raise flvid.VideoPageParseError('Could not find video url. Aborting.')

            swfconf = None
            for script_element in r:
                for pattern in patterns:
                    m = pattern.search(script_element.text_content())
                    if m is not None:
                        swfconf = json.loads(m.group(1))
                        break
                if swfconf is not None:
                    break

            if swfconf is None:
                return None

            video             = self.video_class()
            video.format_urls = self._fmt_to_url_map(swfconf)
            return video

    def _get_title(self, tree):
        r = tree.xpath("//meta[@property='og:title']")
        for elem in r:
            return elem.get('content').strip()

        r = tree.xpath("//span[@id='eow-title']")
        for elem in r:
            return elem.text_content().strip()

        raise flvid.VideoPageParseError('Could not determine the title of the video. Aborting')

    def scrape_video(self, url):
        resp, content = httplib2.Http().request(url, 'GET')
        tree = lxml.html.fromstring(content)
        video = self._try_script_elements(tree)
        if video is None:
            video = self._try_embed_element(tree)
        video.title = self._get_title(tree)
        return video

def register():
    flvid.registered_scrapers.append(YouTubeVideoScraper)
