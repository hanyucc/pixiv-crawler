import requests
from bs4 import BeautifulSoup
# import GetHtml
import time
import os
import shutil
from fake_useragent import UserAgent

ua = UserAgent()
se = requests.session()
base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
}
return_to = 'http://www.pixiv.net/'

def login():
    post_key_html = se.get(base_url, headers=headers).text
    post_key_soup = BeautifulSoup(post_key_html, 'lxml')
    post_key = post_key_soup.find('input')['value']
    data = {
        'pixiv_id': pixiv_id,
        'password': password,
        'return_to': return_to,
        'post_key': post_key
    }
    se.post(login_url, data=data, headers=headers)


def downloadOneImage(imgInfo, entireUrl):
    imgInfo = imgInfo.find('img')
    imgSrc = imgInfo['src']
    title = imgInfo['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

    if os.path.isfile('images/' + title + '.png') or os.path.isfile('images/' + title + '.jpg'):
        return

    begin = imgSrc.find('img/')
    end = imgSrc.find('_master')
    then = imgSrc[:].find('.')

    imgOrigSrc = 'https://i.pximg.net/img-original/' + imgSrc[begin:end] + imgSrc[end + then + 2:]

    srcHeaders = headers
    srcHeaders['Referer'] = entireUrl

    try:
        img = requests.get(imgOrigSrc, headers=srcHeaders).content
    except Exception:
        print('Download image failed. Trying again.')
        try:
            img = requests.get(imgOrigSrc, headers=srcHeaders).content
        except Exception:
            print('Download image failed. Skipping image.')

    try:
        if img.decode('UTF-8').find('404 Not'):
            imgOrigSrc = imgOrigSrc[:-3] + 'png'
            print(imgOrigSrc)
            try:
                img = requests.get(imgOrigSrc, headers=srcHeaders).content
            except Exception:
                print('Download image failed. Trying again.')
                try:
                    img = requests.get(imgOrigSrc, headers=srcHeaders).content
                except Exception:
                    print('Download image failed. Skipping image.')

            try:
                os.mkdir('images')
            except Exception:
                pass

            with open('images/' + title + '.png', 'ab') as image:
                image.write(img)

    except Exception:
        print(imgOrigSrc)

        try:
            os.mkdir('images')
        except Exception:
            pass

        with open('images/' + title + '.jpg', 'ab') as image:
            image.write(img)

    time.sleep(3)


def downloadMultiImages(title, imgUrl):
    title = title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
    replace = imgUrl.find('illust_id=')
    newUrl = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=' + imgUrl[replace + 10:]
    html = se.get(newUrl, headers=headers, timeout=10)
    soup = BeautifulSoup(html.text, 'lxml')
    total = soup.find('span', class_='total')
    newUrl = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' + imgUrl[replace + 10:]

    print(newUrl)

    for i in range(int(total.text) + 1):
        multiUrl = newUrl + '&page=' + str(i)
        html = se.get(multiUrl, headers=headers, timeout=10)
        soup = BeautifulSoup(html.text, 'lxml')
        imgSrc = soup.find('img')['src']
        type = imgSrc[-4:]

        srcHeaders = headers
        srcHeaders['Referer'] = multiUrl

        if os.path.isfile('images/' + title + '/' + title + '-' + str(i) + type):
            continue

        try:
            img = requests.get(imgSrc, headers=srcHeaders).content
        except Exception:
            print('Download image failed. Trying again.')
            try:
                img = requests.get(imgSrc, headers=srcHeaders).content
            except Exception:
                print('Download image failed. Skipping image.')

        try:
            os.mkdir('images')
        except Exception:
            pass

        try:
            os.mkdir('images/' + title)
        except Exception:
            pass

        with open('images/' + title + '/' + title + '-' + str(i) + type, 'ab') as image:
            image.write(img)
            print(multiUrl)

        time.sleep(3)


def getImg(item):
    headers['Referer'] = ua.random

    baseUrl = 'https://www.pixiv.net'
    imgUrl = item.find('a', class_='work')['href']
    # print(baseUrl+imgUrl)

    html = se.get(baseUrl + imgUrl, headers=headers, timeout=10)

    soup = BeautifulSoup(html.text, 'lxml')
    imgInfo = soup.find('div', class_='works_display')\
        .find('div', class_='_layout-thumbnail ui-modal-trigger')

    if imgInfo:
        downloadOneImage(imgInfo, baseUrl + imgUrl)
    elif multiImages == 'n':
        return
    else:
        try:
            title = soup.find('div', class_='works_display')\
                .find('div', class_='_layout-thumbnail')\
                .find('img')['alt']
            imgInfo = soup.find('div', class_='works_display') \
                .find('a', class_='multiple')
        except Exception:
            return

        if imgInfo:
            downloadMultiImages(title, imgUrl)


rawKeyword = input('Enter search keyword: ')
searchKeyword = requests.utils.quote(rawKeyword)

startPage = [int(x) for x in input('Enter start page: ').split()][0]
endPage = [int(x) for x in input('Enter end page: ').split()][0]

favThresh = [int(x) for x in input('Enter least number of bookmarks accepted: ').split()][0]
multiImages = input('Accept multiple images (manga)? (y/n): ').split()[0]

pixiv_id = input('Enter pixiv id or email: ')
password = input('Enter pixiv password: ')

login()

try:
    lastKeyword = open('htmls/.lastKeyword').read()
    if lastKeyword != searchKeyword:
        deleteFolders = input('htmls and images folders need to be deleted to continue. (y/n): ')
        if deleteFolders == 'y':
            shutil.rmtree('htmls')
            shutil.rmtree('images')
        else:
            raise SystemExit
except Exception:
    try:
        deleteFolders = input('htmls and images folders need to be deleted to continue. (y/n): ')
        if deleteFolders == 'y':
            shutil.rmtree('htmls')
            shutil.rmtree('images')
        else:
            raise SystemExit
    except Exception:
        pass

for i in range(startPage, endPage + 1):
    if os.path.isfile('htmls/page-' + str(i) + '.html'):
        continue

    url ='https://www.pixiv.net/search.php?s_mode=s_tag&word=' + searchKeyword + '&p='\
        + str(i)
    print(url)

    html = se.get(url, headers=headers, timeout=3)

    try:
        os.mkdir('htmls')
        with open('htmls/.lastKeyword', 'w') as f:
            f.write(searchKeyword)
    except Exception:
        pass

    with open('htmls/page-' + str(i) + '.html', 'w', encoding='UTF-8') as file:
        file.write(html.text)

    time.sleep(5)


cnt = 0

for i in range(startPage, endPage + 1):
    print('\nStarting page ' + str(i) + '\n')
    html = open('htmls/page-' + str(i) + '.html', encoding='UTF-8').read()
    soup = BeautifulSoup(html, 'lxml')
    itemList = soup.find_all('li', class_='image-item')

    for item in itemList:
        favLabel = item.find('a', class_='bookmark-count _ui-tooltip')
        if favLabel:
            favNum = int(favLabel.text)
            if favNum >= favThresh:
                getImg(item)
                cnt += 1

print('\n' + str(cnt) + ' in total\n')
