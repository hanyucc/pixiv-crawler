import requests
from bs4 import BeautifulSoup
import getHtml
import os
import time

se = requests.session()

base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
	}
pixiv_id = ''
password = ''
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

    begin = imgSrc.find('img/')
    end = imgSrc.find('_master')
    then = imgSrc[:].find('.')

    imgOrigSrc = 'https://i.pximg.net/img-original/' + imgSrc[begin:end] + imgSrc[end + then + 2:]

    srcHeaders = headers
    srcHeaders['Referer'] = entireUrl

    try:
        img = requests.get(imgOrigSrc, headers=srcHeaders).content
    except Exception as e:
        print('Download image failed. Trying again.')
        try:
            img = requests.get(imgOrigSrc, headers=srcHeaders).content
        except Exception as e:
            print('Download image failed. Skipping image.')

    try:
        if img.decode('UTF-8').find('404 Not'):
            imgOrigSrc = imgOrigSrc[:-3] + 'png'
            print(imgOrigSrc)
            try:
                img = requests.get(imgOrigSrc, headers=srcHeaders).content
            except Exception as e:
                print('Download image failed. Trying again.')
                try:
                    img = requests.get(imgOrigSrc, headers=srcHeaders).content
                except Exception as e:
                    print('Download image failed. Skipping image.')

            title = imgInfo['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
                .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

            try:
                os.mkdir('images')
            except Exception as e:
                doNothing = 0

            with open('images/' + title + '.png', 'ab') as image:
                image.write(img)

    except Exception as e:
        print(imgOrigSrc)

        title = imgInfo['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
            .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

        try:
            os.mkdir('images')
        except Exception as e:
            doNothing = 0

        with open('images/' + title + '.jpg', 'ab') as image:
            image.write(img)

    time.sleep(3)


def downloadMultiImages(title, imgUrl):
    replace = imgUrl.find('illust_id=')
    newUrl = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=' + imgUrl[replace + 10:]
    html = se.get(newUrl, headers=headers, timeout=10)
    soup = BeautifulSoup(html.text, 'lxml')
    total = soup.find('span', class_='total')
    newUrl = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' + imgUrl[replace + 10:]

    print(newUrl)

    for i in range(int(total.text)):
        multiUrl = newUrl + '&page=' + str(i + 1)
        html = se.get(multiUrl, headers=headers, timeout=10)
        soup = BeautifulSoup(html.text, 'lxml')
        imgSrc = soup.find('img')['src']

        srcHeaders = headers
        srcHeaders['Referer'] = multiUrl

        try:
            img = requests.get(imgSrc, headers=srcHeaders).content
        except Exception as e:
            print('Download image failed. Trying again.')
            try:
                img = requests.get(imgSrc, headers=srcHeaders).content
            except Exception as e:
                print('Download image failed. Skipping image.')

        type = imgSrc[-4:]

        try:
            os.mkdir('images')
        except Exception as e:
            doNothing = 0

        title = title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
            .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

        try:
            os.mkdir('images/' + title)
        except Exception as e:
            doNothing = 0

        with open('images/' + title + '/' + str(i + 1) + type, 'ab') as image:
            image.write(img)
            print(i + 1)


        time.sleep(3)


def getImg(item):
    baseUrl = 'https://www.pixiv.net'
    imgUrl = item.find('a', class_='work')['href']

    # print(baseUrl+imgUrl)

    html = se.get(baseUrl + imgUrl, headers=headers, timeout=10)

    soup = BeautifulSoup(html.text, 'lxml')
    imgInfo = soup.find('div', class_='works_display')\
        .find('div', class_='_layout-thumbnail ui-modal-trigger')

    if imgInfo:
        downloadOneImage(imgInfo, baseUrl + imgUrl)
    else:
        try:
            title = soup.find('div', class_='works_display')\
                .find('div', class_='_layout-thumbnail')\
                .find('img')['alt']
            imgInfo = soup.find('div', class_='works_display') \
                .find('div', class_='multiple')
        except Exception as e:
            return

        if imgInfo:
            downloadMultiImages(title, imgUrl)



pixiv_id = getHtml.pixiv_id
password = getHtml.password
pages = getHtml.pages
favThresh = getHtml.favThresh

login()

cnt = 0

for i in range(pages):
    print('\nStarting page ' + str(i + 1) + '\n')
    html = open('htmls/page-' + str(i + 1) + '.html', encoding='UTF-8').read()
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
