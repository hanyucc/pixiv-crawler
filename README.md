# pixiv-crawler
A Pixiv crawler that can filter images by the numbers of bookmarks.

（P站又改网页结构了，气人...）

# Requirements
* Python 3
* Requests
* BeautifulSoup 4
```
pip3 install requests
pip3 install beautifulsoup4
pip3 install lxml
```

Removed proxy version.

# Usage
Either fill in all fields in ```query.json``` (to avoid filling in the same information every time you run the script) or delete the file.

Then, run the script.

```
python3 get_image.py
```
