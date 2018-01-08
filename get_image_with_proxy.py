import requests
import json
import time
import os
import shutil
from bs4 import BeautifulSoup


se = requests.session()

proxies = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.89 Chrome/62.0.3202.89 Safari/537.36'
}


def login(pixiv_id, password):
    base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
    post_key_html = se.get(base_url, headers=headers, proxies=proxies).text
    post_key_soup = BeautifulSoup(post_key_html, 'lxml')
    post_key = post_key_soup.find('input', {'name': 'post_key'})['value']
    data = {
        'pixiv_id': pixiv_id,
        'password': password,
        'post_key': post_key
    }
    se.post(login_url, data=data, headers=headers, proxies=proxies)


def download_one_image(img_info, entire_url):
    img_info = img_info.find('img')
    img_src = img_info['src']
    title = img_info['alt'].replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

    if os.path.isfile('images/' + title + '.png') or os.path.isfile('images/' + title + '.jpg'):
        return

    begin = img_src.find('img/')
    end = img_src.find('_master')
    then = img_src[:].find('.')

    img_orig_src = 'https://i.pximg.net/img-original/' + img_src[begin:end] + img_src[end + then + 2:]

    src_headers = headers
    src_headers['Referer'] = entire_url

    try:
        img = se.get(img_orig_src, headers=src_headers, proxies=proxies).content
    except Exception:
        print('Download image failed. Trying again.')
        try:
            img = se.get(img_orig_src, headers=src_headers, proxies=proxies).content
        except Exception:
            print('Download image failed. Skipping image.')
            time.sleep(3)
            return

    try:
        if img.decode('UTF-8').find('404 Not'):
            img_orig_src = img_orig_src[:-3] + 'png'
            print(img_orig_src)
            try:
                img = se.get(img_orig_src, headers=src_headers, proxies=proxies).content
            except Exception:
                print('Download image failed. Trying again.')
                try:
                    img = se.get(img_orig_src, headers=src_headers, proxies=proxies).content
                except Exception:
                    print('Download image failed. Skipping image.')

            try:
                os.mkdir('images')
            except Exception:
                pass

            with open('images/' + title + '.png', 'ab') as image:
                image.write(img)

    except Exception:
        print(img_orig_src)

        try:
            os.mkdir('images')
        except Exception:
            pass

        with open('images/' + title + '.jpg', 'ab') as image:
            image.write(img)

    time.sleep(3)


def download_multi_images(title, illust_id):
    title = title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()
    new_url = 'https://www.pixiv.net/member_illust.php?mode=manga&illust_id=' + illust_id
    html = se.get(new_url, headers=headers, timeout=10, proxies=proxies)
    soup = BeautifulSoup(html.text, 'lxml')
    total = soup.find('span', class_='total')
    new_url = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' + illust_id

    print(new_url)

    for i in range(int(total.text) + 1):
        multi_url = new_url + '&page=' + str(i)
        html = se.get(multi_url, headers=headers, timeout=10, proxies=proxies)
        soup = BeautifulSoup(html.text, 'lxml')
        img_src = soup.find('img')['src']
        type = img_src[-4:]

        src_headers = headers
        src_headers['Referer'] = multi_url

        if os.path.isfile('images/' + title + '/' + title + '-' + str(i) + type):
            continue

        try:
            img = se.get(img_src, headers=src_headers, proxies=proxies).content
        except Exception:
            print('Download image failed. Trying again.')
            try:
                img = se.get(img_src, headers=src_headers, proxies=proxies).content
            except Exception:
                print('Download image failed. Skipping image.')
                continue

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
            print(multi_url)

        time.sleep(3)


def get_img(illust_id, multi_images):
    base_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    img_url = base_url + illust_id

    html = se.get(img_url, headers=headers, timeout=10, proxies=proxies)

    soup = BeautifulSoup(html.text, 'lxml')
    img_info = soup.find('div', class_='works_display')\
        .find('div', class_='_layout-thumbnail ui-modal-trigger')

    if img_info:
        download_one_image(img_info, img_url)
    elif multi_images == 'n':
        return
    else:
        try:
            title = soup.find('div', class_='works_display')\
                .find('div', class_='_layout-thumbnail')\
                .find('img')['alt']
            img_info = soup.find('div', class_='works_display') \
                .find('a', class_='multiple')
        except Exception:
            return

        if img_info:
            download_multi_images(title, img_url)


def main():
    raw_keyword = input('Enter search keyword: ')
    search_keyword = requests.utils.quote(raw_keyword)

    start_page = [int(x) for x in input('Enter start page: ').split()][0]
    end_page = [int(x) for x in input('Enter end page: ').split()][0]

    bookmark_thresh = [int(x) for x in input('Enter least number of bookmarks accepted: ').split()][0]
    multi_images = input('Accept multiple images (manga)? (y/n): ').split()[0]

    pixiv_id = input('Enter pixiv id or email: ')
    password = input('Enter pixiv password: ')

    login(pixiv_id, password)

    try:
        last_keyword = open('htmls/.lastKeyword').read()
        if last_keyword != search_keyword:
            delete_folders = input('htmls and images folders need to be deleted to continue. (y/n): ')
            if delete_folders == 'y':
                try:
                	shutil.rmtree('htmls')
                	shutil.rmtree('images')
                except Exception:
                	pass
            else:
                raise SystemExit
    except Exception:
        try:
            delete_folders = input('htmls and images folders need to be deleted to continue. (y/n): ')
            if delete_folders == 'y':
                try:
                	shutil.rmtree('htmls')
                	shutil.rmtree('images')
                except Exception:
                	pass
            else:
                raise SystemExit
        except Exception:
            raise SystemExit

    headers['Referer'] = 'https://www.pixiv.net/'

    for i in range(start_page, end_page + 1):
        if os.path.isfile('htmls/page-' + str(i) + '.html'):
            continue

        url ='https://www.pixiv.net/search.php?s_mode=s_tag&word=' + search_keyword + '&p='\
            + str(i)
        print(url)

        html = se.get(url, headers=headers, timeout=10, proxies=proxies)

        try:
            os.mkdir('htmls')
            with open('htmls/.lastKeyword', 'w') as f:
                f.write(search_keyword)
        except Exception:
            pass

        with open('htmls/page-' + str(i) + '.html', 'w', encoding='UTF-8') as file:
            file.write(html.text)

        time.sleep(3)

    cnt = 0

    for i in range(start_page, end_page + 1):
        print('\nStarting page ' + str(i) + '\n')
        html = open('htmls/page-' + str(i) + '.html', encoding='UTF-8').read()
        soup = BeautifulSoup(html, 'lxml')
        data_items = json.loads(soup.find('input', id='js-mount-point-search-result-list')['data-items'])

        for item in data_items:
            if item['bookmarkCount'] >= bookmark_thresh:
                get_img(item['illustId'], multi_images)
                cnt += 1

    print('\n' + str(cnt) + ' in total\n')


if __name__ == '__main__':
    main()
