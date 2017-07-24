import requests
from bs4 import BeautifulSoup
import os
import time

headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36"
}
se = requests.session()


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

            title = imgInfo['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
                .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

            try:
                os.mkdir('images')
            except Exception:
                pass

            with open('images/' + title + '.png', 'ab') as image:
                image.write(img)

    except Exception:
        print(imgOrigSrc)

        title = imgInfo['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
            .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
        
        try:
            os.mkdir('images')
        except Exception:
            pass

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
        except Exception:
            print('Download image failed. Trying again.')
            try:
                img = requests.get(imgSrc, headers=srcHeaders).content
            except Exception:
                print('Download image failed. Skipping image.')

        type = imgSrc[-4:]

        try:
            os.mkdir('images')
        except Exception:
            pass

        title = title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
            .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

        try:
            os.mkdir('images/' + title)
        except Exception:
            pass

        with open('images/' + title + '/' + str(i + 1) + type, 'ab') as image:
            image.write(img)
            print(i + 1)

        time.sleep(3)
