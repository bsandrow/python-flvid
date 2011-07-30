
import sys
import optparse
import flvid

def run():
    parser = optparse.OptionParser()
    parser.add_option(
            '-o','--outfile',
            dest='filename',
            metavar='FILE',
            help='Save video to FILE')
    parser.add_option(
            '--format-info',
            dest='display_info',
            action='store_true',
            help='Display info for the format that corresponds with the current url')
    parser.add_option(
            '-f','--format',
            dest='formatlist',
            metavar='FORMAT_LIST',
            help='Specify the preferred format list as a string of comma-separated values. This option will be ignored for videos that only have a single format.')
    opts, args = parser.parse_args()

    if len(args) < 1:
        print 'ERROR: A URL is required!'
        parser.print_help()
        sys.exit(1)
    url = args.pop()

    if opts.display_info:
        cls = flvid.determine_scraper(url)
        print 'Scraper     : %s' % cls.__name__
        print 'Video Class : %s' % cls.video_class.__name__
        print 'Format Order: %s' % ', '.join(cls.video_class.format_fallback_order)
        print 'Formats     : %s' % '\n    '.join([''] + cls.video_class.format_strings())
        sys.exit()


    video = flvid.get_video(url)
    if opts.formatlist:
        video.format_fallback_order = opts.formatlist.split(',')

    video.download_video(dest=(opts.filename or None))


