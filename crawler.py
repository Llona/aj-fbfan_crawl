import requests
from dateutil.parser import parse
import shutil
from datetime import datetime
import const_define
import os

FB_GRAPH_API_URL = r'https://developers.facebook.com/tools/explorer/'

def start_to_crawl_fanpage(token, fanpage_dic_ld, form_foldername, datetime_limt, queue_h):
    # -----Start to crawl fb fan page data-----
    # get_token()
    for fanpage_name, fanpage_id in fanpage_dic_ld.items():
        # print('%s - %s' % (fanpage_name, fanpage_id))
        # print("開始抓取粉絲頁: %s" % fanpage_name)
        queue_h.put(['info', "開始抓取粉絲頁: %s" % fanpage_name])
        posts = start_crawl(token, fanpage_id, datetime_limt, queue_h)
        if posts:
            # self.setlog("抓取結束!產生報表中", "info2")
            queue_h.put(['info2', "抓取結束! 產生報表中"])
            # 檔案輸出
            create_form(posts, fanpage_name, form_foldername, queue_h)
        else:
            # print("粉絲頁: %s 讀取失敗, 換個token再試試吧" % fanpage_name)
            queue_h.put(['error', "粉絲頁: %s 讀取失敗, 換個token再試試吧" % fanpage_name])

    # print('所有工作已完成!!')
    queue_h.put(['end', '所有工作已完成!!'])


def start_crawl(token, fanpage_id, datetime_limt, queue_h):
    # print(token)
    # 建立空的list
    posts = []
    try:
        # 抓取貼文時間、ID、內文、分享內容
        res = requests.get('https://graph.facebook.com/v2.11/{}/posts?limit=100&access_token={}'.format(fanpage_id, token))
    except:
        # self.setlog("讀取失敗", "error")
        return

    page = 1
    while 'paging' in res.json():
        # self.setlog("正在抓取第%d頁" % page, "info2")
        # print('正在抓取第%d頁' % page)
        queue_h.put(['info2', '正在抓取第%d頁' % page])

        for post in res.json()['data']:
            post_date = parse(post['created_time'])
            post_date = post_date.replace(tzinfo=None)
            if post_date < datetime.strptime(datetime_limt, const_define.DATETIME_FORMAT):
                return posts

            # 透過貼文ID來抓取讚數與分享數
            try:
                res2 = requests.get('https://graph.facebook.com/v2.11/{}?fields=comments.limit(0).summary(true),likes.limit(0).summary(true), shares&access_token={}'.format(post['id'], token))
            except:
                # print('粉絲頁讀取失敗, 換個token再試一次吧')
                queue_h.put(['error', "粉絲頁讀取失敗, 換個token再試試吧"])
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
            temp_dic['content'] = str(post.get('message'))
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


def store_file_to_folder(file, folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    shutil.copy2(file, folder_path)


def create_form(posts, fanpage_name, form_foldername, queue_h):
    # copy temp.html to log folder
    store_file_to_folder('temp_form.xls', form_foldername)
    os.rename(('%s\\temp_form.xls' % form_foldername), ('%s\\%s.xls' % (form_foldername, fanpage_name)))
    excel_full_path = ('%s\\%s.xls' % (form_foldername, fanpage_name))

    # write to html
    try:
        readfile_excel_lh = open(excel_full_path, 'r', encoding='utf8')
        excel_content = str(readfile_excel_lh.read())
        readfile_excel_lh.close()
    except Exception as ex:
        queue_h.put(['error', "Error! 讀取excel檔發生錯誤!請確認%s目錄有temp_form.xls且內容正確" % const_define.TITLE])
        return

    if posts:
        for post in posts:
            excel_content = excel_content.replace('{{next_item}}', const_define.form_template_need_repeat)

            excel_content = excel_content.replace('{{post_date}}', str(post['date']))
            excel_content = excel_content.replace('{{post_content}}', str(post['content']))
            excel_content = excel_content.replace('{{post_likes}}', str(post['likes']))
            excel_content = excel_content.replace('{{post_shares}}', str(post['shares']))
            excel_content = excel_content.replace('{{post_comments}}', str(post['comments']))
            excel_content = excel_content.replace('{{post_id}}', str(post['id']))

        excel_content = excel_content.replace('{{next_item}}', '')

        try:
            writhfile_excel_lh = open(excel_full_path, 'w', encoding='utf8')
            writhfile_excel_lh.write(excel_content)
            writhfile_excel_lh.close()
            # print("已產生excel檔, 路徑:" + excel_full_path)
            queue_h.put(['info2', "已產生excel檔, 路徑:%s" % excel_full_path])

        except Exception as ex:
            # print("Error! 寫入excel檔發生錯誤!請確認目錄有temp_form.xls且內容正確", 'error')
            queue_h.put(['error', "Error! 寫入excel檔發生錯誤!請確認目錄有temp_form.xls且內容正確"])
            return
