import re
import flvid
import httplib2
import json
import lxml.html

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

    def scrape_video(self, url):
        resp, content = httplib2.Http().request(url, 'GET')
        tree = lxml.html.fromstring(content)

        r = tree.xpath('''//span[@id='eow-title']''')
        if len(r) > 1:
            raise flvid.VideoPageParseError('XPath matched multiple video titles. Aborting.')
        if len(r) < 1:
            raise flvid.VideoPageParseError('Could not determine title of video. Aborting.')
        title = r[0].text_content().strip()

        r = tree.xpath('/html/body/script[4]')
        if len(r) > 1:
            raise flvid.VideoPageParseError('XPath matched multiple <script> elements. Aborting.')
        if len(r) < 1:
            raise flvid.VideoPageParseError('Could not find video url. Aborting.')

        # Two different possible <script> setups, both with the same JSON
        # passed through as the video player config.
        m = re.search(r'var swfConfig = (\{".*"\});', lxml.html.tostring(r[0]))
        if m is None:
            m = re.search(
                    r'''yt\.setConfig\(\{\s*'PLAYER_CONFIG':\s*(\{".*"\})\s*\}\);''',
                    lxml.html.tostring(r[0]),
                    re.S | re.M)

        if m is None:
            raise flvid.VideoPageParseError('Could not find a video to extract on the page')

        swfconf = json.loads(m.group(1))

        video             = YouTubeVideo()
        video.format_urls = self._fmt_to_url_map(swfconf)
        video.title       = title

        return video

def register():
    flvid.registered_scrapers.append(YouTubeVideoScraper)
