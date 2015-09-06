# __author__ = 'traitravinh'
import re
from BeautifulSoup import BeautifulSoup
################################## Vkool #########################################
NAME = "Xemphimso"
BASE_URL = "http://xemphimso.com/"
SEARH_URL = 'http://xemphimso.com/tim-kiem/%s'
DEFAULT_ICO = 'icon-default.png'
SEARCH_ICO = 'icon-search.png'
NEXT_ICO = 'icon-next.png'
##### REGEX #####
####################################################################################################

def Start():
    ObjectContainer.title1 = NAME
    HTTP.CacheTime = CACHE_1HOUR
    # HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:22.0) Gecko/20100101 Firefox/22.0'
    HTTP.Headers['X-Requested-With'] = 'XMLHttpRequest'
####################################################################################################

@handler('/video/xemphimso', NAME)
def MainMenu():
    oc = ObjectContainer()
    oc.add(InputDirectoryObject(
        key=Callback(Search),
        title='SEARCH',
        thumb=R(SEARCH_ICO)
    ))
    try:
        for a in BeautifulSoup(str(BeautifulSoup(HTTP.Request(BASE_URL,cacheTime=3600).content)('div',{'id':'nav_menu'})[0]))('li'):
            asoup = BeautifulSoup(str(a))
            try:
                atitle = asoup('a')[0].contents[0]
                alink = asoup('a')[0]['href']
                # addDir(atitle.encode('utf-8'),alink,1,logo,False,None,'')
                oc.add(DirectoryObject(
                    key=Callback(Category, title=atitle, catelink=alink),
                    title=atitle,
                    thumb=R(DEFAULT_ICO)
                ))
            except:pass

    except Exception, ex:
        Log("******** Error retrieving and processing latest version information. Exception is:\n" + str(ex))

    return oc
####################################################################################################

@route('/video/xemphimso/search')
def Search(query=None):
    if query is not None:
        url = SEARH_URL % ((String.Quote(query, usePlus=True)))
        Log(url)
        return Category(query, url)

@route('/video/xemphimso/category')
def Category(title, catelink):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(catelink,cacheTime=3600).content
    soup = BeautifulSoup(link)
    for item in BeautifulSoup(str(soup('ul',{'class':'cfv'})[0]))('li'):
        isoup = BeautifulSoup(str(item))
        ititle = isoup('a')[0]['title']
        ilink = isoup('a')[0]['href']
        img = isoup('img')[0]['src']
        oc.add(DirectoryObject(
            key=Callback(Server, title=ititle, svlink=ilink, svthumb=img, inum=None),
            title=ititle,
            thumb=img
        ))
    try:
        for p in BeautifulSoup(str(soup('div',{'class':'pagination'})[0]))('a'):
            psoup = BeautifulSoup(str(p))
            plink = psoup('a')[0]['href']
            ptitle = psoup('a')[0].contents[0]
            oc.add(DirectoryObject(
                key=Callback(Category, title=ptitle, catelink=plink),
                title=ptitle,
                thumb=R(NEXT_ICO)
            ))
    except:pass

    return oc

####################################################################################################
@route('/video/xemphimso/server')
def Server(title, svlink, svthumb, inum):
    oc = ObjectContainer(title2=title)
    link = HTTP.Request(svlink,cacheTime=3600).content
    ptag = re.compile('<p class="bt">(.+?)</p>').findall(link)[0]
    link = BeautifulSoup(ptag)('a',{'class':'btn-watch'})[0]['href']
    try:
        for e in BeautifulSoup(str(BeautifulSoup(HTTP.Request(link,cacheTime=3600).content)('td',{'class':'listep'})[0]))('a'):
            esoup = BeautifulSoup(str(e))
            etitle = esoup('a')[0].contents[0].next
            elink = esoup('a')[0]['href']
            # addLink(etitle.encode('utf-8'),elink,3,iconimage,gname)
            oc.add(createMediaObject(
                url=elink,
                title=etitle.encode('utf-8'),
                thumb=svthumb,
                rating_key=etitle
            ))
    except:pass

    return oc

@route('/video/xemphimso/createMediaObject')
def createMediaObject(url, title,thumb,rating_key,include_container=False,includeRelatedCount=None,includeRelated=None,includeExtras=None):
    container = Container.MP4
    video_codec = VideoCodec.H264
    audio_codec = AudioCodec.AAC
    audio_channels = 2
    track_object = EpisodeObject(
        key = Callback(
            createMediaObject,
            url=url,
            title=title,
            thumb=thumb,
            rating_key=rating_key,
            include_container=True
        ),
        title = title,
        thumb=thumb,
        rating_key=rating_key,
        items = [
            MediaObject(
                parts=[
                    PartObject(key=Callback(PlayVideo, url=url))
                ],
                container = container,
                video_resolution = '720',
                video_codec = video_codec,
                audio_codec = audio_codec,
                audio_channels = audio_channels,
                optimized_for_streaming = True
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects=[track_object])
    else:
        return track_object

@indirect
def PlayVideo(url):
    url = videolinks(url)
    if str(url).find('youtube')!=-1:
        oc = ObjectContainer(title2='Youtube Video')
        # idregex = r'https?://www.youtube.com/(?:embed/|watch\?v=)'+r'(.+?(?=\?)|.+)'
        # VideoUrl = re.compile(idregex).findall(url)[0]
        # url='https://www.youtube.com/watch?v='+VideoUrl
        oc.add(VideoClipObject(
            url=url,
            title='Youtube video',
            thumb=R(DEFAULT_ICO)
        ))
        return oc
    else:
        return IndirectResponse(VideoClipObject, key=url)

def videolinks(url):
    link = HTTP.Request(url,cacheTime=3600).content
    vlinks = re.compile('urlplayer = "(.+?)&pre').findall(link)[0]
    subvlinks = HTTP.Request(vlinks,cacheTime=3600).content
    filelink = re.compile('"file":"(.+?),"label"').findall(subvlinks)
    if len(filelink)==0:
        filelink = re.compile('"file":"(.+?)","').findall(subvlinks)

    if len(filelink)>1:
        flinks = filelink[len(filelink)-1].replace('\\','').strip('"')
    else:
        flinks = filelink[0].replace('\\','').strip('"')
    return flinks

####################################################################################################
