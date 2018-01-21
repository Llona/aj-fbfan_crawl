# -*- coding: utf-8 -*-
import requests
from dateutil.parser import parse
from datetime import datetime, timedelta
import os
import shutil
import re

# 指定要抓到那一天
DATETIME_LIMIT = '2018-01-1 00-00-00'
DATETIME_FORMAT = "%Y-%m-%d %H-%M-%S"

# https://developers.facebook.com/tools/explorer/
# 取得token與粉絲頁id
token = 'EAACEdEose0cBAFB5oeSBQGThozwAIpoauE8Sgfwa2GmBsLdph0EqcGG6BZBgIUbeZBRX4nmRsUnSpvu02ZB4Fm4hk3vtF3h4NAqwAfUiLwZA5cXJLea3RSZCbIbT1FiVm3p5ZAvmtS6zwtnW9SluZCAkpRW8fdeMpSYuk1epQlrQ22ZBgoxc9a770eZAQTdWWBb2BamZCHZAYaz1QZDZD'
# 粉絲專頁ID
fanpage_id = '615156555285597'

form_template_need_repeat = \
'    <tr>\n'\
'        <th align="center">{{post_date}}</th>\n'\
'        <th align="center">{{post_content}}</th>\n'\
'        <th align="center">{{post_likes}}</th>\n'\
'        <td align="center">{{post_shares}}</td>\n'\
'        <th align="center">{{post_comments}}</th>\n\n'\
'        <th align="center">{{post_id}}</th>\n\n'\
'    </tr>\n'\
'{{next_item}}'


def start_crawl():
    # 建立空的list
    posts = []

    # 抓取貼文時間、ID、內文、分享內容
    res = requests.get('https://graph.facebook.com/v2.11/{}/posts?limit=100&access_token={}'.format(fanpage_id, token))

    page = 1
    while 'paging' in res.json():
        print('目前正在抓取第%d頁' % page)

        for post in res.json()['data']:
            post_date = parse(post['created_time'])
            post_date = post_date.replace(tzinfo=None)
            if post_date < datetime.strptime(DATETIME_LIMIT, DATETIME_FORMAT):
                return posts

            # 透過貼文ID來抓取讚數與分享數
            try:
                res2 = requests.get('https://graph.facebook.com/v2.11/{}?fields=comments.limit(0).summary(true),likes.limit(0).summary(true), shares&access_token={}'.format(post['id'], token))
            except:
                print('粉絲頁讀取失敗, 換個token再試一次吧')
                return

            # 留言數
            if 'comments' in res2.json():
                comments = res2.json()['comments']['summary'].get('total_count')
            else:
                comments = 0

            # 按讚數
            if 'likes' in res2.json():
                likes = res2.json()['likes']['summary'].get('total_count')
            else:
                likes = 0

            # 分享數
            if 'shares' in res2.json():
                shares = res2.json()['shares'].get('count')
            else:
                shares = 0

            temp_dic = {}
            temp_dic['date'] = parse(post['created_time'])
            temp_dic['content'] = post.get('message')
            temp_dic['likes'] = likes
            temp_dic['shares'] = shares
            temp_dic['comments'] = comments
            temp_dic['id'] = post['id']

            posts.append(temp_dic)

        if 'next' in res.json()['paging']:
            res = requests.get(res.json()['paging']['next'])
            page += 1
        else:
            return posts

def store_file_to_folder(file, back_folder):
    if not os.path.exists(back_folder):
        os.makedirs(back_folder)
    shutil.copy2(file, back_folder)


def create_form(posts):
    form_foldername = re.sub(r":", '.', str(datetime.utcnow() + timedelta(hours=8)))
    # copy temp.html to log folder
    store_file_to_folder('temp_form.xls', form_foldername)
    os.rename(('%s\\temp_form.xls' % form_foldername), ('%s\\form.xls' % form_foldername))
    excel_full_path = ('%s\\form.xls' % form_foldername)

    # write to html
    try:
        readfile_excel_lh = open(excel_full_path, 'r', encoding='utf8')
        excel_content = str(readfile_excel_lh.read())
        readfile_excel_lh.close()
    except Exception as ex:
        #self.setlog("Error! 讀取excel檔發生錯誤! "
        #            "請確認" + TITLE + "目錄有temp_form.xls且內容正確", 'error')
        print('Error! 讀取excel檔發生錯誤! 請確認目錄有temp_form.xls且內容正確')
        return

    for post in posts:
        excel_content = excel_content.replace('{{next_item}}', form_template_need_repeat)

        excel_content = excel_content.replace('{{post_date}}', str(post['date']))
        excel_content = excel_content.replace('{{post_content}}', str(post['content']))
        excel_content = excel_content.replace('{{post_likes}}', str(post['likes']))
        excel_content = excel_content.replace('{{post_shares}}', str(post['shares']))
        excel_content = excel_content.replace('{{post_comments}}', str(post['comments']))
        excel_content = excel_content.replace('{{post_id}}', str(post['id']))

    excel_content = excel_content.replace('{{next_item}}', '')
    # excel_content = excel_content.replace('{{post_date}}', '')
    # excel_content = excel_content.replace('{{post_content}}', '')
    # excel_content = excel_content.replace('{{post_likes}}', '')
    # excel_content = excel_content.replace('{{post_shares}}', '')
    # excel_content = excel_content.replace('{{post_comments}}', '')
    # excel_content = excel_content.replace('{{post_id}}', '')

    try:
        # writhfile_html_lh = open('test.html', 'w')
        writhfile_excel_lh = open(excel_full_path, 'w', encoding='utf8')
        writhfile_excel_lh.write(excel_content)
        writhfile_excel_lh.close()

    except Exception as ex:
        print("Error! 寫入excel檔發生錯誤!請確認目錄有temp_form.xls且內容正確", 'error')
        return

if __name__ == '__main__':
    posts = start_crawl()
    print('抓取結束!')
    # 檔案輸出
    create_form(posts)
    print('已產生excel檔')
    # df = pd.DataFrame(posts)
    # df.columns = ['貼文時間', '貼文ID', '貼文內容', '讚數', '分享數', '留言數']
    # df.to_csv('aaa.csv', index=False)
    #
    # test2 = pd.read_csv('aaa.csv')
    # print(test2)

