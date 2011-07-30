flvid
=====

A framework for building web video scrapers. The main narrative goes like this:

1. You pass a URL to a scraper
2. The scraper extracts the video link and associated metadata and stores it in
   a object that is a sub-class of flvid.Video.
3. The Video object has methods on it for interacting with the associated
   metadata, including downloading the video to a file.

Usage
-----

    import flvid
    video = flvid.get_video('http://www.youtube.com/?v=afgdfgdfgfag')
    video.download_video(dest='/tmp')

Copyright
---------

Copyright (c) 2011 Brandon Sandrowicz under the MIT license. See LICENSE.txt.
