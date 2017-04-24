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
    'User-Agent': 'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
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

    time.sleep(2)

def getImg(item):
    baseUrl = 'https://www.pixiv.net'
    imgUrl = item.find('a', class_='work')['href']

    # print(baseUrl+imgUrl)

    html = se.get(baseUrl + imgUrl, headers=headers, timeout=10)

    soup = BeautifulSoup(html.text, 'lxml')
    imgInfo = soup.find('div', attrs={'class', 'works_display'})\
        .find('div', class_='_layout-thumbnail ui-modal-trigger')

    if imgInfo:
        downloadOneImage(imgInfo, baseUrl + imgUrl)

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
