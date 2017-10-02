import cookielib, urllib, urllib2, time,sys
from bs4 import BeautifulSoup
import os

"""
https://github.com/ttki3n/download_playlist_CSN

Download the whole playlist from chiasenhac.vn
The codes may not run correctly if they change the web format ^^!

Got inspiration from
https://github.com/doanguyen/CSN-playlist-extractor

"""

account = {'username':'username_of_CSN','password':'password_of_CSN'}
proxy_protocol = 'https' # http, https etc
proxy_user = 'ABCBCBCB%40:hehehe@proxy.company.org:1234'  # username:password@proxy_host:port. If any fields have '@' character, you should replace it by %40

NEED_LOGIN=0 # the last time I checked, CSN didn't require login for downloading anymore
NEED_PROXY=0

quality_map = {'flac':'Lossless_FLAC', '500':'500kbps_M4A', '320':'320kbps_MP3', '128':'128kbps_MP3', '32':'32kbps_M4A'}
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'

save_folder = 'music'


cookies = cookielib.CookieJar()

if (NEED_PROXY == 0):
    g_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),urllib2.HTTPHandler(debuglevel=0),urllib2.HTTPSHandler(debuglevel=0),urllib2.HTTPCookieProcessor(cookies))
else:
    proxy_handler = urllib2.ProxyHandler({proxy_protocol : proxy_user})
    g_opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),urllib2.HTTPHandler(debuglevel=0),urllib2.HTTPSHandler(debuglevel=0),urllib2.HTTPCookieProcessor(cookies), proxy_handler)    

g_opener.addheaders = [('User-Agent', user_agent)]

def download_CSN(argv):

    lists = get_playlist(argv[1])
    quality = quality_map[argv[2]]    
    
    if (len(lists) > 0):
        print "There are %s song(s) in the playlist, waiting for the download link." %(len(lists))
        if (NEED_LOGIN == 1):
            login(account)
        
        downloadLinks = getlink(lists, quality)
        
        for link in downloadLinks:
            download_file(link, save_folder)
    else:
        print "ERROR ::: Can not found any song in the playlist !!!"


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
    f = open("test.txt", "wb")
    for link in links:
        html = g_opener.open(link).read()        
        document = BeautifulSoup(html, 'html.parser')
        donwload_part = (document.find(id="downloadlink2").find_all('a'))
        for line in donwload_part:
            link = line.get('href')
            if link.find(quality) != -1:
                result.append(link.replace(' ','%20'))
                f.write(link)
                break
    
    f.close()
    return result

def download_file(link, save_folder):
    print 'Downloading file :', link
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)    
    response = g_opener.open(link)
    response_header = response.info()
    if check_is_valid_file_from_headers(response_header) == False:
        return
    filename = get_filename_from_url(link)
    with open(save_folder + "/" + filename, "wb") as ofile:
        ofile.write(response.read())

def get_filename_from_url(link):
    a1 = link.split('&v5=')
    return urllib.unquote(a1[1])

def check_is_valid_file_from_headers(headers):
    result = True
    if (headers['Content-Type'] != 'applicaton/octet-stream'):
        print 'ERROR ::: response headers :: Content-Type is ', headers['Content-Type']
        #result = False
    
    return result
    
def login(account):
    print "Logging ..."
    url = 'http://chiasenhac.vn/login.php'
    values = {'username' : account['username'],'password' : account['password'],'autologin' : 'on','redirect' : '','login' : "%C4%90%C4%83ng+nh%E1%BA%ADp"}
    data = urllib.urlencode(values)
    return g_opener.open(url, data)


if __name__ == '__main__':
    download_CSN(sys.argv)
