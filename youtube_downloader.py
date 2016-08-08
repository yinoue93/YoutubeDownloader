# -*- coding: utf-8 -*-
import sys
import os
import shutil
import urllib
import urllib2
import re
import subprocess
import threading
import time
import mutagen.id3

from mutagen.mp4 import MP4
from mutagen.mp4 import MP4Cover
from argparse import ArgumentParser
from multiprocessing import Lock
from bs4 import BeautifulSoup

# Example:
#   python youtube_downloader.py -q 'ゆず' -x False -N songs -m 1:00:00 -i 2:00

# usage: youtube_downloader.py [-h] -q TEXTTOSEARCH -x TOITUNES [-n NUM_VIDEOS]
#                             [-m MAXTIME] [-i MINTIME] -N FOLDERNAME
#
#youtube_downloader.py [Args] [Options] Detailed options -h or --help
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -q TEXTTOSEARCH, --query TEXTTOSEARCH
#                        Keyword to search
#  -x TOITUNES, --export TOITUNES
#                        Export to Itunes
#  -n NUM_VIDEOS, --num NUM_VIDEOS
#                        Number of videos to download
#  -m MAXTIME, --max MAXTIME
#                        Maximum video length
#  -i MINTIME, --min MINTIME
#                        Minimum video length
#  -N FOLDERNAME, --name FOLDERNAME
#                        Name of the Folder

def audio_downloader(input_str, c, sema, printLock):
    os.system('youtube-dl.exe -f 140 -q -o /temp/' + str(c) + '##'
              +'%(title)s.%(ext)s '+input_str)
    with printLock:
        print str(c)+": done"
    sema.release()
    exit()

def update_youtube_dl():
    versionReg = '[0-9]+\.[0-9]+\.[0-9]+'
    url = "http://youtube-dl.org/"
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, "html.parser")

    # download the videos
    thread_list = []
    count = 0
    for txt in soup.findAll('div'):
        if '(' in txt.text:
            latestVer = re.search(versionReg, txt.text).group()
            print 'Latest Version of youtube-dl: '+latestVer
            break

    try:
        versionResp = subprocess.check_output('youtube-dl.exe --version', shell=True)
        loadedVer = re.search(versionReg, versionResp).group()
        print 'Current Version of youtube-dl: '+loadedVer
    except:
        print 'youtube-dl not found...'
        loadedVer = ''

    if loadedVer != latestVer:
        print 'Updating youtube-dl...'
        for vid in soup.findAll('a'):
            if 'youtube-dl.exe' == vid.text:
                youDL_path = os.path.join(url,vid['href'])
                print 'Downloading from... '+youDL_path

                urllib.urlretrieve(youDL_path,youDL_path.split('/')[-1])
                break
    print 'Correct version of youtube-dl loaded'

if __name__ == "__main__":
    # delete the temp directory
    if os.path.exists('temp'):
        shutil.rmtree('temp')

    desc = u'{0} [Args] [Options]\nDetailed options -h or --help'.format(__file__)
    parser = ArgumentParser(description=desc)

    parser.add_argument(
        '-q', '--query',
        type = str,
        dest = 'textToSearch',
        required = True,
        help = 'Keyword to search'
    )

    parser.add_argument(
        '-x', '--export',
        type = str,
        dest = 'toItunes',
        required = True,
        help = 'Export to Itunes'
    ) 

    parser.add_argument(
        '-n', '--num',
        type = int,
        dest = 'num_videos',
        default = 20,
        help = 'Number of videos to download'
    ) 

    parser.add_argument(
        '-m', '--max',
        type = str,
        dest = 'maxTime',
        default = '23:59:59',
        help = 'Maximum video length'
    ) 

    parser.add_argument(
        '-i', '--min',
        type = str,
        dest = 'minTime',
        default = '0:0:0',
        help = 'Minimum video length'
    ) 

    parser.add_argument(
        '-N', '--name',
        type = str,
        dest = 'folderName',
        required = True,
        help = 'Name of the Folder'
    ) 

    args = parser.parse_args()

    textToSearch = args.textToSearch.decode('sjis')
    if args.folderName:
        folderName = args.folderName.decode('sjis')
    else:
        folderName = textToSearch
    num_videos = args.num_videos

    if len(args.maxTime.split(':'))==3:
        maxTime = time.strptime(args.maxTime,'%H:%M:%S')
    else:
        maxTime = time.strptime(args.maxTime,'%M:%S')
    if len(args.minTime.split(':'))==3:
        minTime = time.strptime(args.minTime,'%H:%M:%S')
    else:
        minTime = time.strptime(args.minTime,'%M:%S')

    update_youtube_dl()
    
    max_thread = 10
    sema = threading.Semaphore(max_thread)

    if 'www.youtube.com' in textToSearch:
        url = textToSearch
        count = 0
        printLock = Lock()
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")
        thread_list = []

        img_tags = soup.findAll(attrs={'class':'yt-thumb-clip'})
        for img_tag in img_tags:
            if '.jpg' in img_tag.img['src'] or '.png' in img_tag.img['src']:
                img_url = img_tag.img['src'].replace('&','&amp;')
                break

        # download the videos
        for vid in soup.findAll(attrs={'class':'yt-uix-scroller-scroll-unit'}):
            try:
                url_ext = re.search('/watch\?v=[_a-zA-Z0-9-]+',vid.a['href']).group()
                url_str = 'https://www.youtube.com' + url_ext
                with printLock:
                    print str(count)+': '+url_str
                sema.acquire(True)
                th = threading.Thread(target=audio_downloader, 
                                      args=(url_str,count,sema,printLock))

                thread_list.append(th)
                th.start()
                count += 1
                if count == num_videos:
                    moreAudio = False
                    break
            except Exception as e:
                print e

    else:
        moreAudio = True
        query = urllib.quote(textToSearch.encode('utf-8'))
        url = "https://www.youtube.com/results?search_query=" + query

        count = 0
        printLock = Lock()
        while moreAudio:
            response = urllib2.urlopen(url)
            html = response.read()
            soup = BeautifulSoup(html, "html.parser")

            # download the videos
            thread_list = []
            for vid in soup.findAll(attrs={'class':'yt-uix-sessionlink        spf-link '}):
                try:
                    vidLength = vid.find(attrs={'class':'video-time'}).text
                    if len(vidLength.split(':'))==3:
                        vidLength = time.strptime(vidLength,'%H:%M:%S')
                    else:
                        vidLength = time.strptime(vidLength,'%M:%S')

                    if ("list" not in vid['href']) and ("channel" not in vid['href']) \
                                        and (vidLength<maxTime) and (vidLength>minTime):
                        url_str = 'https://www.youtube.com' + vid['href']
                        if 'watch?v=' not in url_str:
                            continue
                        with printLock:
                            print str(count)+': '+url_str
                        sema.acquire(True)
                        th = threading.Thread(target=audio_downloader, 
                                              args=(url_str,count,sema,printLock))
                        thread_list.append(th)
                        th.start()
                        count += 1
                        if count == num_videos:
                            moreAudio = False
                            break
                except:
                    pass

            # gather information for the next page
            for grp in soup.findAll(attrs={'class':'yt-uix-button-content'}):
                if grp.text and ('Next ' in grp.text):
                    url = "https://www.youtube.com" + grp.parent['href']
                    break

        # cover image for the album
        url = 'https://www.youtube.com/results?search_query='+query
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")

        for vid in soup.findAll(attrs={'class':'yt-thumb-simple'}):
            try:
                img_url = vid.find('img')['data-thumb']
                img_url = img_url.replace('&','&amp;')
                break
            except:
                pass

    with printLock:
        print "All threads dispatched. Waiting..."
    for th in thread_list:
        th.join()

    # make the directory for the created files
    try:
        if args.toItunes!='True':
            os.mkdir(folderName)
    except:
        print 'Folder already exists...'

    fd = urllib2.urlopen(img_url)
    # Drop the entire PIL part
    covr = MP4Cover(fd.read(), getattr(MP4Cover,
                'FORMAT_PNG' if img_url.endswith('png') else 'FORMAT_JPEG'))
    fd.close()
    for root, dirs, files in os.walk("temp"):
        for f in files:
            try:
                [songOrder,filename] = f.decode('sjis').split('##')
                songOrder = int(songOrder)

                # add tags to the downloaded m4a's
                m = MP4('temp/'+f)
                m['\xa9alb'] = folderName+'-Youtube'
                m['\xa9ART'] = folderName
                m['covr'] = [covr]
                m['trkn'] = [(songOrder+1,num_videos)]
                m.save()

                srcpath = os.path.join(root, f)
                srcpath = srcpath.replace("\\","/")

                if args.toItunes=='True':
                    folderPath = 'D:/iTunes/iTunes/iTunes Media/Automatically Add to iTunes/'+filename
                    shutil.copyfile(srcpath, folderPath)
                else:
                    shutil.copyfile(srcpath, folderName+'/'+filename)
            except Exception as e:
                print e
                pass

    # delete the temp directory
    shutil.rmtree(u'temp')

    print "done"

