import requests
from bs4 import BeautifulSoup
import os
import time

se = requests.session()

base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
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

rawKeyword = input('Enter search keyword: ')
searchKeyword = requests.utils.quote(rawKeyword)

startPage = [int(x) for x in input('Enter start page: ').split()][0]
endPage = [int(x) for x in input('Enter end page: ').split()][0]

favThresh = [int(x) for x in input('Enter least number of bookmarks accepted: ').split()][0]

pixiv_id = input('Enter pixiv id or email: ')
password = input('Enter pixiv password: ')

login()

for i in range(startPage, endPage + 1):
    if os.path.isfile('htmls/page-' + str(i) + '.html'):
        continue

    url ='https://www.pixiv.net/search.php?s_mode=s_tag&word=' + searchKeyword + '&p='\
        + str(i)
    print(url)

    html = se.get(url, headers=headers, timeout=3)

    try:
        os.mkdir('htmls')
    except Exception:
        pass

    with open('htmls/page-' + str(i) + '.html', 'w', encoding='UTF-8') as file:
        file.write(html.text)

    time.sleep(3)
