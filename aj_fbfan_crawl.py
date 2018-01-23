# -*- coding: utf-8 -*-
import requests
from dateutil.parser import parse
from datetime import datetime, timedelta
import os
import shutil
# import re
from collections import OrderedDict
from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font
import tkinter.messagebox
from tkinter.filedialog import askopenfilename

import configparser
from enum import Enum

# 指定要抓到那一天
DATETIME_LIMIT = '2018-01-1 00-00-00'
DATETIME_FORMAT = "%Y-%m-%d %H-%M-%S"

TODAY_DATE_DIC = {}
TODAY_DATE_DIC['YEAR'] = (datetime.now().strftime("%Y"))
TODAY_DATE_DIC['MON'] = (datetime.now().strftime("%m"))
TODAY_DATE_DIC['DAY'] = (datetime.now().strftime("%d"))

SETTING_NAME = "Settings.ini"
FANPAGE_NAME = "fanpage.sdb"
FANPAGE_GET_LIST = "fanpageGet.txt"

VERSION = "v0.0.1"
TITLE = 'AJ FanPage Crawler - %s' % VERSION
# https://developers.facebook.com/tools/explorer/

FB_GRAPH_API_URL = r'https://developers.facebook.com/tools/explorer/'

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


class error_Type(Enum):
    NORMAL = 'NORMAL'  # define normal state
    FILE_ERROR = 'FILE_RW_ERROR'  # define file o/r/w error type


class AJFanPageCrawl(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        self.top = self.winfo_toplevel()
        self.style = Style()
        self.user_input_token = ''
        self.token_ini = ''
        self.create_widgets()

    def create_widgets(self):
        self.style = Style()
        self.style.configure('Tlog_frame.TLabelframe', font=('iLiHei', 10))
        self.style.configure('Tlog_frame.TLabelframe.Label', font=('iLiHei', 10))
        self.log_frame = LabelFrame(self.top, text='LOG', style='Tlog_frame.TLabelframe')
        self.log_frame.place(relx=0.01, rely=0.283, relwidth=0.973, relheight=0.708)

        self.style.configure('Tuser_input_frame.TLabelframe', font=('iLiHei', 10))
        self.style.configure('Tuser_input_frame.TLabelframe.Label', font=('iLiHei', 10))
        self.user_input_frame = LabelFrame(self.top, text='輸入', style='Tuser_input_frame.TLabelframe')
        self.user_input_frame.place(relx=0.01, rely=0.011, relwidth=0.973, relheight=0.262)

        self.VScroll1 = Scrollbar(self.log_frame, orient='vertical')
        self.VScroll1.place(relx=0.967, rely=0.010, relwidth=0.022, relheight=0.936)

        self.HScroll1 = Scrollbar(self.log_frame, orient='horizontal')
        self.HScroll1.place(relx=0.01, rely=0.940, relwidth=0.958, relheight=0.055)

        self.log_txtFont = Font(font=('iLiHei', 10))
        self.log_txt = Text(self.log_frame, wrap='none', state="disabled", xscrollcommand=self.HScroll1.set, yscrollcommand=self.VScroll1.set, font=self.log_txtFont)
        self.log_txt.place(relx=0.01, rely=0.010, relwidth=0.958, relheight=0.936)
        # self.log_txt.insert('1.0', '')
        self.HScroll1['command'] = self.log_txt.xview
        self.VScroll1['command'] = self.log_txt.yview

        self.style.configure('Tupdate_button.TButton', font=('iLiHei', 9))
        self.start_update_button = Button(self.user_input_frame, text='Start', command=self.crawl_gen_form, style='Tupdate_button.TButton')
        self.start_update_button.place(relx=0.710, rely=0.788, relwidth=0.105, relheight=0.200)

        # self.browser_button = Button(self.user_input_frame, text='Browser', command=self.browser_diag, style='Tget_wiki_button.TButton')
        # self.browser_button.place(relx=0.820, rely=0.160, relwidth=0.105, relheight=0.200)

        self.style.configure('Tversion_label.TLabel', anchor='e', font=('iLiHei', 9))
        self.version_label = Label(self.user_input_frame, text=VERSION, state='disable', style='Tversion_label.TLabel')
        self.version_label.place(relx=0.843, rely=0.87, relwidth=0.147, relheight=0.13)

        self.style.configure('Ttoken_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.token_label = Label(self.user_input_frame, text='輸入token', style='Ttoken_label.TLabel')
        self.token_label.place(relx=0.01, rely=0.010, relwidth=0.200, relheight=0.166)

        self.user_input_token = self.read_config(SETTING_NAME, 'General', 'token')
        if self.user_input_token == error_Type.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + TITLE + "\n", parent=self.top)
            sys.exit(0)
        self.token_entryVar = StringVar(value=self.user_input_token)
        self.token_entry = Entry(self.user_input_frame, textvariable=self.token_entryVar, font=('iLiHei', 10))
        self.token_entry.place(relx=0.01, rely=0.180, relwidth=0.80, relheight=0.180)

        self.style.configure('Tlogin_name_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.login_name_label = Label(self.user_input_frame, text='輸入管理員帳號', style='Tlogin_name_label.TLabel')
        self.login_name_label.place(relx=0.01, rely=0.400, relwidth=0.200, relheight=0.166)

        self.user_input_login_name = self.read_config(SETTING_NAME, 'General', 'login_name')
        if self.user_input_login_name == error_Type.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n"
                                         "請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + TITLE + "\n", parent=self.top)
            sys.exit(0)

        self.login_name_entryVar = StringVar(value=self.user_input_login_name)
        self.login_name_entry = Entry(self.user_input_frame, textvariable=self.login_name_entryVar, font=('iLiHei', 10), state='disable')
        self.login_name_entry.place(relx=0.01, rely=0.550, relwidth=0.30, relheight=0.180)

        self.style.configure('Tlogin_password_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.login_password_label = Label(self.user_input_frame, text='輸入管理員密碼', style='Tlogin_password_label.TLabel')
        self.login_password_label.place(relx=0.35, rely=0.400, relwidth=0.200, relheight=0.166)

        self.__user_input_login_password = self.read_config(SETTING_NAME, 'General', 'login_password')
        if self.__user_input_login_password == error_Type.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n""請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + TITLE + "\n", parent=self.top)
            sys.exit(0)
        self.login_password_entryVar = StringVar(value=self.__user_input_login_password)
        self.login_password_entry = Entry(self.user_input_frame, show="*", textvariable=self.login_password_entryVar, font=('iLiHei', 10), state='disable')
        self.login_password_entry.place(relx=0.35, rely=0.550, relwidth=0.30, relheight=0.180)

        self.style.configure('Tyear_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.year_label = Label(self.user_input_frame, text='西元年:', style='Tyear_label.TLabel')
        self.year_label.place(relx=0.01, rely=0.788, relwidth=0.100, relheight=0.166)

        self.year_entryVar = StringVar(value=TODAY_DATE_DIC['YEAR'])
        self.year_entry = Entry(self.user_input_frame, textvariable=self.year_entryVar, font=('iLiHei', 10))
        self.year_entry.place(relx=0.080, rely=0.788, relwidth=0.060, relheight=0.180)

        self.style.configure('Tmon_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.mon_label = Label(self.user_input_frame, text='月份:', style='Tmon_label.TLabel')
        self.mon_label.place(relx=0.150, rely=0.788, relwidth=0.100, relheight=0.166)

        self.mon_entryVar = StringVar(value=TODAY_DATE_DIC['MON'])
        self.mon_entry = Entry(self.user_input_frame, textvariable=self.mon_entryVar, font=('iLiHei', 10))
        self.mon_entry.place(relx=0.200, rely=0.788, relwidth=0.040, relheight=0.180)

        self.style.configure('Tday_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.day_label = Label(self.user_input_frame, text='日:', style='Tday_label.TLabel')
        self.day_label.place(relx=0.250, rely=0.788, relwidth=0.100, relheight=0.166)

        self.day_entryVar = StringVar(value=TODAY_DATE_DIC['DAY'])
        self.day_entry = Entry(self.user_input_frame, textvariable=self.day_entryVar, font=('iLiHei', 10))
        self.day_entry.place(relx=0.280, rely=0.788, relwidth=0.040, relheight=0.180)

        self.log_txt.tag_config("error", foreground="#CC0000")
        self.log_txt.tag_config("info", foreground="#008800")
        self.log_txt.tag_config("info2", foreground="#404040")

        # self.top.protocol("WM_DELETE_WINDOW", self.close_frame)

    def browser_diag(self):
        path = askopenfilename(initialdir=os.path.split(self.token_entry.get())[0], parent=self.top)
        path = os.path.normpath(path)

        if path and path != '.':
            self.token_entryVar.set(path)

    def read_config(self, filename, section, key):
        try:
            config_lh = configparser.ConfigParser()
            file_ini_lh = open(filename, 'r', encoding='utf16')
            config_lh.read_file(file_ini_lh)
            file_ini_lh.close()
            return config_lh.get(section, key)
        except:
            self.setlog("Error! 讀取ini設定檔發生錯誤! "
                        "請在" + TITLE + "目錄下使用UTF-16格式建立 " + filename, 'error')
            return error_Type.FILE_ERROR.value

    def write_config(self, filename, sections, key, value):
        try:
            config_lh = configparser.ConfigParser()
            file_ini_lh = open(filename, 'r', encoding='utf16')
            config_lh.read_file(file_ini_lh)
            file_ini_lh.close()

            file_ini_lh = open(filename, 'w', encoding='utf16')
            config_lh.set(sections, key, value)
            config_lh.write(file_ini_lh)
            file_ini_lh.close()
        except Exception as ex:
            self.setlog("Error! 寫入ini設定檔發生錯誤! "
                        "請在" + TITLE + "目錄下使用UTF-16格式建立 " +filename, 'error')
            return error_Type.FILE_ERROR.value

    def setlog(self, string, level=None):
        self.log_txt.config(state="normal")

        if (level != 'error') and (level != 'info') and (level != 'info2'):
            level = ""

        # self.log_txt.insert(INSERT, "%s\n" % string, level)
        self.log_txt.insert(END, "%s\n" % string, level)
        # -----scroll to end of text widge-----
        self.log_txt.see(END)
        self.top.update_idletasks()

        self.log_txt.config(state="disabled")

    def setlog_large(self, string, level=None):
        self.log_txt.insert(INSERT, "%s\n" % string, level)
        # -----scroll to end of text widge-----
        self.log_txt.see(END)
        self.top.update_idletasks()

    def crawl_gen_form(self):
        # -----Clear text widge for log-----
        self.log_txt.config(state="normal")
        self.log_txt.delete('1.0', END)
        self.log_txt.config(state="disable")

        # -----Check user input in GUI-----
        self.user_input_token = self.token_entry.get()
        if self.user_input_token == "":
            tkinter.messagebox.showinfo("message", "請輸入token", parent=self.top)
            return

        # -----get config ini file setting-----
        self.token_ini = self.read_config(SETTING_NAME, 'General', 'token')

        if self.token_ini == error_Type.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "錯誤! 讀取ini設定檔發生錯誤! "
                                         "請在" + TITLE + "目錄下使用UTF-16格式建立 " + SETTING_NAME)
            return

        # -----Store user input path, name and password into Setting.ini config file-----
        if not self.user_input_token == self.token_ini:
            self.setlog("新的路徑設定寫入設定檔: " + SETTING_NAME, "info")
            # print("path not match, write new path to ini")
            w_file_stat_lv = self.write_config(SETTING_NAME, 'General', 'token', self.user_input_token)

            if w_file_stat_lv == error_Type.FILE_ERROR.value:
                tkinter.messagebox.showerror("Error",
                                             "錯誤! 寫入ini設定檔發生錯誤! "
                                             "請在" + TITLE + "目錄下使用UTF-16格式建立 " + SETTING_NAME, parent=self.top)
                return

        # -----Get all fan page list-----
        fanpage_all_dic_ld = OrderedDict()
        file_fanpage_h = open(FANPAGE_NAME, encoding='utf8')
        while True:
            fanpage_all_content = file_fanpage_h.readline()
            if fanpage_all_content:
                re_h = re.match(r'(.+);(.+)', fanpage_all_content)
                fanpage_all_dic_ld[re_h.group(1)] = re_h.group(2)
            else:
                break
        file_fanpage_h.close()

        # ----get need to crawl fan page name list and get id from fanpage_all_dic_ld----
        fanpage_dic_ld = OrderedDict()
        file_fanpage_get_h = open(FANPAGE_GET_LIST, encoding='utf8')
        for fanpage_get_content in file_fanpage_get_h.readlines():
            fanpage_get_content = fanpage_get_content.strip('\n')
            # print(fanpage_get_content)
            if fanpage_get_content in fanpage_all_dic_ld.keys():
                # print(fanpage_all_dic_ld[fanpage_get_content])
                fanpage_dic_ld[fanpage_get_content] = fanpage_all_dic_ld[fanpage_get_content]
            else:
                self.setlog("粉絲頁: %s 不在資料庫中, 請確認%s與%s內容" % (fanpage_get_content, FANPAGE_NAME, FANPAGE_GET_LIST), "error")
                return
        file_fanpage_get_h.close()

        # ----create form sore folder-----
        form_foldername = re.sub(r":", '.', str(datetime.utcnow() + timedelta(hours=8)))

        # -----gen date time limt string-----
        # print(self.day_entry.get())
        mon = int(self.mon_entry.get())
        if mon and mon < 10:
                mon = str('0%d' % mon)
        day = str(int(self.day_entry.get()))
        datetime_limt = ('%s-%s-%s 00-00-00' % (self.year_entry.get(), mon, day))
        print(datetime_limt)
        return

        # -----Start to crawl fb fan page data-----
        # get_token()
        for fanpage_name, fanpage_id in fanpage_dic_ld.items():
            print('%s - %s' % (fanpage_name, fanpage_id))
            self.setlog("開始抓取粉絲頁: %s" % fanpage_name, "info2")
            posts = self.start_crawl(self.user_input_token, fanpage_id, datetime_limt)
            if posts:
                self.setlog("抓取結束!產生報表中", "info")
                # 檔案輸出
                self.create_form(posts, fanpage_name, form_foldername)
            else:
                self.setlog("粉絲頁: %s 讀取失敗, 換個token再試試吧" % fanpage_name, "error")

    def start_crawl(self, token, fanpage_id, datetime_limt):
        # print(token)
        # 建立空的list
        posts = []
        try:
            # 抓取貼文時間、ID、內文、分享內容
            res = requests.get('https://graph.facebook.com/v2.11/{}/posts?limit=100&access_token={}'.format(fanpage_id, token))
        except:
            self.setlog("讀取失敗", "error")
            return

        page = 1
        while 'paging' in res.json():
            print('正在抓取第%d頁' % page)
            self.setlog("正在抓取第%d頁" % page, "info2")

            for post in res.json()['data']:
                post_date = parse(post['created_time'])
                post_date = post_date.replace(tzinfo=None)
                if post_date < datetime.strptime(datetime_limt, DATETIME_FORMAT):
                    return posts

                # 透過貼文ID來抓取讚數與分享數
                try:
                    res2 = requests.get('https://graph.facebook.com/v2.11/{}?fields=comments.limit(0).summary(true),likes.limit(0).summary(true), shares&access_token={}'.format(post['id'], token))
                except:
                    print('粉絲頁讀取失敗, 換個token再試一次吧')
                    self.setlog("目粉絲頁讀取失敗, 換個token再試一次吧", "error")
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

    def store_file_to_folder(self, file, folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        shutil.copy2(file, folder_path)

    def create_form(self, posts, fanpage_name, form_foldername):

        # copy temp.html to log folder
        self.store_file_to_folder('temp_form.xls', form_foldername)
        os.rename(('%s\\temp_form.xls' % form_foldername), ('%s\\%s.xls' % (form_foldername, fanpage_name)))
        excel_full_path = ('%s\\%s.xls' % (form_foldername, fanpage_name))

        # write to html
        try:
            readfile_excel_lh = open(excel_full_path, 'r', encoding='utf8')
            excel_content = str(readfile_excel_lh.read())
            readfile_excel_lh.close()
        except Exception as ex:
            self.setlog("Error! 讀取excel檔發生錯誤!"
                        "請確認" + TITLE + "目錄有temp_form.xls且內容正確", 'error')
            return

        if posts:
            for post in posts:
                excel_content = excel_content.replace('{{next_item}}', form_template_need_repeat)

                excel_content = excel_content.replace('{{post_date}}', str(post['date']))
                excel_content = excel_content.replace('{{post_content}}', str(post['content']))
                excel_content = excel_content.replace('{{post_likes}}', str(post['likes']))
                excel_content = excel_content.replace('{{post_shares}}', str(post['shares']))
                excel_content = excel_content.replace('{{post_comments}}', str(post['comments']))
                excel_content = excel_content.replace('{{post_id}}', str(post['id']))

            excel_content = excel_content.replace('{{next_item}}', '')

            try:
                # writhfile_html_lh = open('test.html', 'w')
                writhfile_excel_lh = open(excel_full_path, 'w', encoding='utf8')
                writhfile_excel_lh.write(excel_content)
                writhfile_excel_lh.close()
                print('已產生excel檔')
                self.setlog("已產生excel檔, 路徑:" + excel_full_path, "info")

            except Exception as ex:
                print("Error! 寫入excel檔發生錯誤!請確認目錄有temp_form.xls且內容正確", 'error')
                return


def check_all_file_status():
    if not os.path.exists(SETTING_NAME):
        return False
    if not os.path.exists('icons\\main.ico'):
        return False
    return True


if __name__ == '__main__':
    # -----MessageBox will create tkinter, so create correct setting tkinter first
    root = Tk()
    root.title(TITLE)
    root.iconbitmap('icons\\main.ico')

    SETTING_NAME = "%s\\%s" % (os.getcwd(), SETTING_NAME)

    if not check_all_file_status():
        tkinter.messagebox.showerror("Error", "遺失必要檔案! \n\n請確認目錄有以下檔案存在, 或 "
                                              "重新安裝: " + TITLE + "\n"
                                              "1. " + SETTING_NAME + "\n"
                                              "2. icons\\main.ico")
        sys.exit(0)

    try:
        # -----Get setting from Settings.ini-----
        file_ini_h = open(SETTING_NAME, encoding='utf16')
        config_h = configparser.ConfigParser()
        config_h.read_file(file_ini_h)
        config_h.clear()
        file_ini_h.close()
    except:
        tkinter.messagebox.showerror("Error",
                                     "讀取設定檔 " + SETTING_NAME + " 錯誤!\n"
                                     "請確認檔案格式為UTF-8 (unicode format) 或重新安裝" + TITLE + "\n")
        sys.exit(0)

    # -----Start GUI class-----
    root.geometry('784x614')
    app = AJFanPageCrawl(master=root)
    # -----Start main loop-----
    app.mainloop()
