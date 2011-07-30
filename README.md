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
    video = flvid.get_video('http://www.example.com/afgdfgdfgfag')
    video.download_video(dest='/tmp')

Legal Note
----------

This framework is created under the assumption that it is the user's
responsibility to determine whether their copying falls under fair use, or that
they have permission to create copies of said videos.

Roadmap
-------

* I need to put some TLC into flvid.app

Copyright
---------

Copyright (c) 2011 Brandon Sandrowicz under the MIT license. See LICENSE.txt.
