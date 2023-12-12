import requests
from bs4 import BeautifulSoup
import pandas as pd

# 搜尋關鍵字
keyword = '失智症'

# 設定 cookie
cookies = {'over18': '1'}

# 建立一個空的 DataFrame 來儲存資料
data = {'看板': [], '內容': [], '留言內容': [] , '留言數': [], '愛心數': []} 

# 開始搜尋文章
for page in range(1, 11):  # 假設你想要搜尋前 10 頁的文章
    url = f'https://www.ptt.cc/bbs/Gossiping/search?page={page}&q={keyword}'

    # 使用 requests 下載網頁內容，並帶入 cookies
    response = requests.get(url, cookies=cookies)

    # 檢查是否成功取得網頁內容
    if response.status_code == 200:
        html = response.text
    else:
        print(f"無法取得網頁內容: {url}")
        continue

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html, 'html.parser')

    # 找到文章列表中的每一篇文章
    articles = soup.find_all('div', class_='r-ent')

    # 逐一處理每篇文章
    for article in articles:
        # 取得文章連結
        link = article.find('div', class_='title').a['href']
        article_url = 'https://www.ptt.cc' + link

        # 再次發送 request 來取得文章內容
        response = requests.get(article_url, cookies=cookies)

        if response.status_code == 200:
            article_html = response.text
            article_soup = BeautifulSoup(article_html, 'html.parser')

            # 提取看板
            board = article_soup.find('span', class_='article-meta-tag', string='看板').find_next('span', class_='article-meta-value').text

            # 提取留言內容
            comments = article_soup.find_all('div', class_='push')
            comment_content = '\n'.join([comment.text for comment in comments])

            # 提取留言數量和愛心數量
            push_count = len(article_soup.find_all('div', class_='push'))
            heart_count = len(article_soup.find_all('span', class_='hl push-tag'))

            # 提取標題主旨
            title_main = article_soup.find('span', class_='article-meta-value').text

            # 提取標題和內容
            _, _, main_content = title_main.partition(' - ')
            content = article_soup.find(id='main-content').text

            data['看板'].append(board)
            data['內容'].append(main_content + '\n' + content)
            data['留言內容'].append(comment_content)
            data['留言數'].append(push_count)
            data['愛心數'].append(heart_count)
            
            
        else:
            print(f"無法取得文章內容: {article_url}")

# 將資料建立為 DataFrame
df = pd.DataFrame(data)

# 將 DataFrame 存為 Excel
df.to_excel('ptt_articles.xlsx', index=False)

# 或存為文字檔
df.to_csv('ptt_articles.txt', index=False, sep='\t', encoding='utf-8')
