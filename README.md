# youtube_downloader.py
Downloads music from youtube with keywords or playlist url, organize them as an album, and imports them in iTunes.
```
 Example:
   python youtube_downloader.py -q 'ゆず' -x False -N songs -m 1:00:00 -i 2:00

 usage: youtube_downloader.py [-h] -q TEXTTOSEARCH -x TOITUNES [-n NUM_VIDEOS]
                             [-m MAXTIME] [-i MINTIME] -N FOLDERNAME

youtube_downloader.py [Args] [Options] Detailed options -h or --help

optional arguments:
  -h, --help            show this help message and exit
  -q TEXTTOSEARCH, --query TEXTTOSEARCH
                        Keyword to search
  -x TOITUNES, --export TOITUNES
                        Export to Itunes
  -n NUM_VIDEOS, --num NUM_VIDEOS
                        Number of videos to download
  -m MAXTIME, --max MAXTIME
                        Maximum video length
  -i MINTIME, --min MINTIME
                        Minimum video length
  -N FOLDERNAME, --name FOLDERNAME
                        Name of the Folder
```

## Details:
* **TEXTTOSEARCH** - Keyword used to download the Youtube videos, or a playlist url
* **TOITUNES** - TRUE to import the downloaded music in iTunes. FALSE otherwise.
* **NUM_VIDEOS** - Number of videos to download. Defaults to 20.
* **MINTIME,MAXTIME** - Min/max time the song can be. Any songs outside of this range are not downloaded.
* **FOLDERNAME** - Album name to store to.

## Album Synthesis
* **Song Order** - is organized by the order in which the video shows up in the downloaded HTML file.
* **Album Name** - Corresponds to the FOLDERNAME parameter.
* **Album Cover** - Thumbnail of one of the videos downloaded.