import requests
from bs4 import BeautifulSoup
import GetHtml
import ImageUtils

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

def getImg(item):
    baseUrl = 'https://www.pixiv.net'
    imgUrl = item.find('a', class_='work')['href']

    # print(baseUrl+imgUrl)

    html = se.get(baseUrl + imgUrl, headers=headers, timeout=10)

    soup = BeautifulSoup(html.text, 'lxml')
    imgInfo = soup.find('div', class_='works_display')\
        .find('div', class_='_layout-thumbnail ui-modal-trigger')

    if imgInfo:
        ImageUtils.downloadOneImage(imgInfo, baseUrl + imgUrl)
    elif multiImages == 'n':
        return
    else:
        try:
            title = soup.find('div', class_='works_display')\
                .find('div', class_='_layout-thumbnail')\
                .find('img')['alt']
            imgInfo = soup.find('div', class_='works_display') \
                .find('div', class_='multiple')
        except Exception:
            return

        if imgInfo:
            ImageUtils.downloadMultiImages(title, imgUrl)

pixiv_id = GetHtml.pixiv_id
password = GetHtml.password
startPage = GetHtml.startPage
endPage = GetHtml.endPage
favThresh = GetHtml.favThresh
multiImages = GetHtml.multiImages

login()

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
