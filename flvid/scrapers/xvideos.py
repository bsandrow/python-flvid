import flvid
import re
import httplib2
import lxml.html
from urllib import unquote

class XvideosVideo(flvid.Video):
    format_fallback_order = [ '1' ]
    all_formats = { '1': { 'type': 'flv', }, }
    video_id = None

    def dest_filebase(self):
        ''' Return the base of the default filename in the form:
        [xvideos].TITLE.VIDEOID '''
        return '[xvideos].%s.%s' % (self.title, self.video_id)

    @classmethod
    def format_strings(cls):
        ''' Return a list of strings that describe each of the formats that
        videos from support xvideos.com '''
        retval = []
        for k,v in cls.all_formats.iteritems():
            retval.append('%s: %s' % (k, v['type']))
        return retval

class XvideosScraper(flvid.Scraper):
    video_class = XvideosVideo
    url_pattern = re.compile(r'^https?://(www\.)?xvideos\.com/video\d+/\w')

    def scrape_video(self, url):
        video = XvideosVideo()

        resp, content = httplib2.Http().request(url, 'GET')
        tree = lxml.html.fromstring(content)

        r = tree.xpath('//title')
        if len(r) > 1:
            raise flvid.VideoPageParseError('Found multiple <title> elements. Aborting.')
        if len(r) < 1:
            raise flvid.VideoPageParseError('Could not find a <title>. Aborting.')
        m = re.search(r'^(.*) - XVIDEOS.COM$', r[0].text_content().strip())
        if m is None:
            raise flvid.VideoPageParseError('Could not extract video title from page title. Aborting.')
        video.title = m.group(1).strip()

        r = tree.xpath('''//embed[@id='flash-player-embed']''')
        if len(r) > 1:
            raise flvid.VideoPageParseError(
                    "Found too many <embed> elements. Don't know which one to look at. Aborting.")
        if len(r) < 1:
            raise flvid.VideoPageParseError('Could not find video player <embed> element on page. Aborting.')

        flashvars         = url_query_2_dict(unquote(r[0].get('flashvars')))
        video.video_id    = flashvars['id_video']
        video.format_urls = {
            '1': '&'.join([
                    flashvars['flv_url'],
                    'ri=%s' % flashvars['ri'],
                    'rs=%s' % flashvars['rs'],
                    'h=%s'  % flashvars['h'],
                ]),
        }

        return video

def url_query_2_dict(query):
    retval = {}
    for param in query.split('&'):
        parts = param.split('=', 1)
        retval[parts[0]] = parts[1]
    return retval

def register():
    flvid.registered_scrapers.append(XvideosScraper)
