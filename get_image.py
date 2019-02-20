import requests
import json
import time
import os
import shutil
from bs4 import BeautifulSoup


se = requests.session()

headers = {
    'Referer': 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.89 Chrome/62.0.3202.89 Safari/537.36'
}


def login(pixiv_id, password):
    base_url = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
    login_url = 'https://accounts.pixiv.net/api/login?lang=zh'
    post_key_html = se.get(base_url, headers=headers).text
    post_key_soup = BeautifulSoup(post_key_html, 'lxml')
    post_key = post_key_soup.find('input', {'name': 'post_key'})['value']
    data = {
        'pixiv_id': pixiv_id,
        'password': password,
        'post_key': post_key
    }
    se.post(login_url, data=data, headers=headers)


def download_one_image(illust_title, illust_src, img_url):
    title = illust_title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

    if os.path.isfile('images/' + title + '.png') or os.path.isfile('images/' + title + '.jpg'):
        return

    src_headers = headers
    src_headers['Referer'] = img_url

    try:
        img = se.get(illust_src, headers=src_headers).content
    except Exception:
        print('Download image failed. Trying again.')
        try:
            img = se.get(illust_src, headers=src_headers).content
        except Exception:
            print('Download image failed. Skipping image.')
            time.sleep(3)
            return

    try:
        if img.decode('UTF-8').find('404 Not'):
            illust_src = illust_src[:-3] + 'png'
            print(illust_src)
            try:
                img = se.get(illust_src, headers=src_headers).content
            except Exception:
                print('Download image failed. Trying again.')
                try:
                    img = se.get(illust_src, headers=src_headers).content
                except Exception:
                    print('Download image failed. Skipping image.')

            with open('images/' + title + '.png', 'ab') as image:
                image.write(img)

    except Exception:
        print(illust_src)

        with open('images/' + title + '.jpg', 'ab') as image:
            image.write(img)

    time.sleep(3)


def download_multi_images(illust_title, page_count, illust_id):
    title = illust_title.replace('?', '_').replace('/', '_').replace('\\', '_').replace('*', '_') \
        .replace('|', '_').replace('>', '_').replace('<', '_').replace(':', '_').replace('"', '_').strip()

    new_url = 'https://www.pixiv.net/member_illust.php?mode=manga_big&illust_id=' + illust_id

    print(new_url)

    for i in range(int(page_count)):
        multi_url = new_url + '&page=' + str(i)
        html = se.get(multi_url, headers=headers, timeout=10)
        soup = BeautifulSoup(html.text, 'lxml')
        img_src = soup.find('img')['src']
        type = img_src[-4:]

        src_headers = headers
        src_headers['Referer'] = multi_url

        if os.path.isfile('images/' + title + '/' + title + '-' + str(i) + type):
            continue

        try:
            img = se.get(img_src, headers=src_headers).content
        except Exception:
            print('Download image failed. Trying again.')
            try:
                img = se.get(img_src, headers=src_headers).content
            except Exception:
                print('Download image failed. Skipping image.')
                continue

        if not os.path.exists('images/' + title):
            os.mkdir('images/' + title)

        with open('images/' + title + '/' + title + '-' + str(i) + type, 'ab') as image:
            image.write(img)
            print(multi_url)

        time.sleep(3)


def get_img(illust_id, multi_images):
    base_url = 'https://www.pixiv.net/member_illust.php?mode=medium&illust_id='
    img_url = base_url + illust_id

    html = se.get(img_url, headers=headers, timeout=10)

    html_str = html.content.decode('utf-8')

    illust_title_begin = html_str.find('"illustTitle":"') + len('"illustTitle":"')
    illust_title_end = html_str.find('","illustComment"')
    illust_title = html_str[illust_title_begin:illust_title_end].encode().decode('unicode-escape').replace('\\/', '/')

    # should be an easier way to do this - -

    illust_src_begin = html_str.find('"original":"') + len('"original":"')
    illust_src_end = html_str.find('"},"tags"')
    illust_src = html_str[illust_src_begin:illust_src_end].encode().decode('unicode-escape').replace('\\/', '/')

    page_count_begin = html_str.find('"pageCount":') + len('"pageCount":')
    page_count_end = html_str.find(',"isBookmarkable"')
    page_count = int(html_str[page_count_begin:page_count_end])

    if page_count == 1:
        download_one_image(illust_title, illust_src, img_url)
    elif not multi_images:
        return
    else:
        download_multi_images(illust_title, page_count, illust_id)


def main():
    if os.path.isfile('query.json'):
        with open('query.json', 'r', encoding='utf-8') as f:
            query = json.load(f)
        raw_keyword = query['keyword']
        search_keyword = requests.utils.quote(raw_keyword)

        start_page = query['start_page']
        end_page = query['end_page']

        bookmark_threshold = query['bookmark_threshold']
        multiple_images = query['multiple_images']

        pixiv_id = query['pixiv_id']
        password = query['password']
    else:
        raw_keyword = input('Enter search keyword: ')
        search_keyword = requests.utils.quote(raw_keyword)

        start_page = [int(x) for x in input('Enter start page: ').split()][0]
        end_page = [int(x) for x in input('Enter end page: ').split()][0]

        bookmark_threshold = [int(x) for x in input('Enter least number of bookmarks accepted: ').split()][0]
        multiple_images = input('Accept multiple images (manga)? (y/n): ').split()[0]

        pixiv_id = input('Enter pixiv id or email: ')
        password = input('Enter pixiv password: ')

    login(pixiv_id, password)

    if os.path.exists('htmls') or os.path.exists('images'):
        continue_task = input('Continue the last task with the same keywords (y)\n'
                              'Or overwrite htmls and images folders (n)\n ')
        if continue_task == 'n':
            try:
                shutil.rmtree('htmls')
                shutil.rmtree('images')
            except Exception:
                pass

    if not os.path.exists('htmls'):
        os.mkdir('htmls')
    if not os.path.exists('images'):
        os.mkdir('images')

    headers['Referer'] = 'https://www.pixiv.net/'

    for i in range(start_page, end_page + 1):
        if os.path.isfile('htmls/page-' + str(i) + '.html'):
            continue

        url ='https://www.pixiv.net/search.php?s_mode=s_tag&word=' + search_keyword + '&p='\
            + str(i)
        print(url)

        html = se.get(url, headers=headers, timeout=10)

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
            print(item)
            if item['bookmarkCount'] >= bookmark_threshold:
                get_img(item['illustId'], multiple_images)
                cnt += 1

    print('\n' + str(cnt) + ' in total\n')


if __name__ == '__main__':
    main()
