import cookielib, urllib, urllib2, time,sys
from bs4 import BeautifulSoup
import os
from datetime import datetime
from threadpool import ThreadPool, _thread_print_lock

from LogHelper import log_helper
logger = log_helper.logger

from config import account_CSN, proxy_dict
"""
https://github.com/ttki3n/download_playlist_CSN

Download the whole playlist from chiasenhac.vn
The codes may not run correctly if they change the web format ^^!

Got inspiration from
https://github.com/doanguyen/CSN-playlist-extractor

"""



NEED_LOGIN = False # the last time I checked, CSN didn't require login for downloading anymore
NEED_PROXY = True
USING_THREAD = True # warning: downloading faster but can get error if server detects as spamming
NUMBER_OF_THREADS = 4
quality_map = {'flac':'Lossless_FLAC', '500':'500kbps_M4A', '320':'320kbps_MP3', '128':'128kbps_MP3', '32':'32kbps_M4A'}
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

save_folder = 'music'
#_thread_print_lock = threading.Lock()

cookies = cookielib.CookieJar()

if (NEED_PROXY == False):
    g_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),urllib2.HTTPHandler(debuglevel=0),urllib2.HTTPSHandler(debuglevel=0),urllib2.HTTPCookieProcessor(cookies))
else:
    proxy_handler = urllib2.ProxyHandler(proxy_dict)
    g_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),urllib2.HTTPHandler(debuglevel=0),urllib2.HTTPSHandler(debuglevel=0),urllib2.HTTPCookieProcessor(cookies), proxy_handler)    

g_opener.addheaders = [('User-Agent', user_agent)]

def download_CSN(argv):

    lists = get_playlist(argv[1])
    quality = quality_map[argv[2]]    
    
    if (len(lists) > 0):
        logger.info("There are %s song(s) in the playlist, waiting for the download link." %(len(lists)))
        if (NEED_LOGIN == True):
            login(account_CSN)
        
        downloadLinks = getlink(lists, quality)
        download_all(downloadLinks, save_folder)
        
    else:
        logger.error("ERROR ::: Can not found any song in the playlist !!!")


def get_playlist(link):
    response = g_opener.open(link)
    
    soup = BeautifulSoup(response.read(), 'html.parser').find(id="playlist").find_all('a')
    single_song = []
    
    for link in soup:
        if "download" in link.get("href"):
            single_song.append(link.get("href"))
    
    return single_song

def getlink(links, quality):
    result = []
    f = open("list_songs.txt", "wb")
    for link in links:
        html = g_opener.open(link).read()        
        document = BeautifulSoup(html, 'html.parser')
        donwload_part = (document.find(id="downloadlink2").find_all('a'))
        for line in donwload_part:
            link = line.get('href')
            if link.find(quality) != -1:
                result.append(link.replace(' ','%20'))
                f.write(link + '\r\n')
                break
    
    f.close()
    return result

def download_all(links, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)
    if USING_THREAD:   
        pool = ThreadPool(NUMBER_OF_THREADS)    
        for link in links:
            with _thread_print_lock:
                logger.debug("download from link: \n  %s \n" % link)
            pool.add_task(download_file, link, save_folder)            
            #pool.add_task(test_func)            
            time.sleep(5)
        pool.wait_completion()   
    else:
        for link in links:
            logger.debug("download from link: \n  %s \n" % link)
            download_file(link, save_folder)

def test_func():
    print "test func"
    
def download_file(link, save_folder):
    logger.debug("starting download file: %s " % link)
    filename = get_filename_from_url(link)    
    with _thread_print_lock:
        logger.info('Downloading file : %s ', filename)    
    response = g_opener.open(link)
    response_header = response.info()
    if check_is_valid_file_from_headers(filename, response_header) == False:
        return
    
    with open(save_folder + "/" + filename, "wb") as ofile:
        ofile.write(response.read())

def get_filename_from_url(link):
    #a1 = link.split('&v5=')
    a1 = link.split('/')
    return urllib.unquote(a1[-1])

def check_is_valid_file_from_headers(filename, headers):
    result = True
    if (headers['Content-Type'] != 'applicaton/octet-stream'):
        with _thread_print_lock:
            logger.error('ERROR ::: file %s with response headers :: Content-Type is %s ' % (filename, headers['Content-Type']))
        #result = False
    
    return result
    
def login(account):
    logger.info("Logging ...")
    url = 'http://chiasenhac.vn/login.php'
    values = {'username' : account['username'],'password' : account['password'],'autologin' : 'on','redirect' : '','login' : "%C4%90%C4%83ng+nh%E1%BA%ADp"}
    data = urllib.urlencode(values)
    return g_opener.open(url, data)


if __name__ == '__main__':
    start = datetime.now()
    download_CSN(sys.argv)
    end = datetime.now()
    
    logger.info("Elapsed time is %s seconds !!!" % ((end-start).total_seconds()))
