# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import os
# import re
from collections import OrderedDict
from tkinter import *
from tkinter.ttk import *
from tkinter.font import Font
import tkinter.messagebox
from tkinter.filedialog import askopenfilename
import configparser
from enum import Enum
from multiprocessing import Process, Queue
from threading import Timer
from robobrowser import RoboBrowser

import const_define
import crawler


def create_process(process_list, args_list):
    process_ll = []
    count = 0

    for process_f in process_list:
        process_ll.append(Process(target=process_f, args=args_list[count]))
        count += 1

    for process in process_ll:
        process.start()

    for process in process_ll:
        process.join()


class ErrorType(Enum):
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
        self.user_input_login_name = ''
        self.login_name_ini = ''
        self.need_timer_restart = False
        self.timer_h = ''
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
        self.start_update_button.place(relx=0.350, rely=0.788, relwidth=0.105, relheight=0.200)

        # self.browser_button = Button(self.user_input_frame, text='Browser', command=self.browser_diag, style='Tget_wiki_button.TButton')
        # self.browser_button.place(relx=0.820, rely=0.160, relwidth=0.105, relheight=0.200)

        self.style.configure('Tversion_label.TLabel', anchor='e', font=('iLiHei', 9))
        self.version_label = Label(self.user_input_frame, text=const_define.VERSION, state='disable', style='Tversion_label.TLabel')
        self.version_label.place(relx=0.843, rely=0.87, relwidth=0.147, relheight=0.13)

        self.style.configure('Ttoken_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.token_label = Label(self.user_input_frame, text='輸入token (保持空白會自動取得token)', style='Ttoken_label.TLabel')
        self.token_label.place(relx=0.01, rely=0.010, relwidth=0.500, relheight=0.166)

        self.user_input_token = self.read_config(SETTING_NAME, 'General', 'token')
        if self.user_input_token == ErrorType.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + const_define.TITLE + "\n", parent=self.top)
            sys.exit(0)
        self.token_entryVar = StringVar(value=self.user_input_token)
        self.token_entry = Entry(self.user_input_frame, textvariable=self.token_entryVar, font=('iLiHei', 10))
        self.token_entry.place(relx=0.01, rely=0.180, relwidth=0.80, relheight=0.180)

        self.style.configure('Tlogin_name_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.login_name_label = Label(self.user_input_frame, text='輸入帳號', style='Tlogin_name_label.TLabel')
        self.login_name_label.place(relx=0.01, rely=0.400, relwidth=0.200, relheight=0.166)

        self.user_input_login_name = self.read_config(SETTING_NAME, 'General', 'login_name')
        if self.user_input_login_name == ErrorType.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n"
                                         "請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + const_define.TITLE + "\n", parent=self.top)
            sys.exit(0)

        self.login_name_entryVar = StringVar(value=self.user_input_login_name)
        self.login_name_entry = Entry(self.user_input_frame, textvariable=self.login_name_entryVar, font=('iLiHei', 10))
        self.login_name_entry.place(relx=0.01, rely=0.550, relwidth=0.30, relheight=0.180)

        self.style.configure('Tlogin_password_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.login_password_label = Label(self.user_input_frame, text='輸入密碼', style='Tlogin_password_label.TLabel')
        self.login_password_label.place(relx=0.35, rely=0.400, relwidth=0.200, relheight=0.166)

        self.__user_input_login_password = self.read_config(SETTING_NAME, 'General', 'login_password')
        if self.__user_input_login_password == ErrorType.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "讀取設定檔 " + SETTING_NAME + " 錯誤!\n""請確認檔案格式為UTF-16 (unicode format) 或重新安裝" + const_define.TITLE + "\n", parent=self.top)
            sys.exit(0)
        self.login_password_entryVar = StringVar(value=self.__user_input_login_password)
        self.login_password_entry = Entry(self.user_input_frame, show="*", textvariable=self.login_password_entryVar, font=('iLiHei', 10))
        self.login_password_entry.place(relx=0.35, rely=0.550, relwidth=0.30, relheight=0.180)

        self.style.configure('Tyear_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.year_label = Label(self.user_input_frame, text='西元年:', style='Tyear_label.TLabel')
        self.year_label.place(relx=0.01, rely=0.788, relwidth=0.100, relheight=0.166)

        self.year_entryVar = StringVar(value=const_define.TODAY_DATE_DIC['YEAR'])
        self.year_entry = Entry(self.user_input_frame, textvariable=self.year_entryVar, font=('iLiHei', 10))
        self.year_entry.place(relx=0.080, rely=0.788, relwidth=0.060, relheight=0.180)

        self.style.configure('Tmon_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.mon_label = Label(self.user_input_frame, text='月份:', style='Tmon_label.TLabel')
        self.mon_label.place(relx=0.150, rely=0.788, relwidth=0.100, relheight=0.166)

        self.mon_entryVar = StringVar(value=const_define.TODAY_DATE_DIC['MON'])
        self.mon_entry = Entry(self.user_input_frame, textvariable=self.mon_entryVar, font=('iLiHei', 10))
        self.mon_entry.place(relx=0.200, rely=0.788, relwidth=0.040, relheight=0.180)

        self.style.configure('Tday_label.TLabel', anchor='w', font=('iLiHei', 10))
        self.day_label = Label(self.user_input_frame, text='日:', style='Tday_label.TLabel')
        self.day_label.place(relx=0.250, rely=0.788, relwidth=0.100, relheight=0.166)

        self.day_entryVar = StringVar(value=const_define.TODAY_DATE_DIC['DAY'])
        self.day_entry = Entry(self.user_input_frame, textvariable=self.day_entryVar, font=('iLiHei', 10))
        self.day_entry.place(relx=0.280, rely=0.788, relwidth=0.040, relheight=0.180)

        self.log_txt.tag_config("error", foreground="#CC0000")
        self.log_txt.tag_config("info", foreground="#008800")
        self.log_txt.tag_config("info2", foreground="#404040")

        root.bind('<Key-Return>', self.press_key_enter)
        self.token_entry.bind("<ButtonRelease-1>", self.select_all)

        # self.top.protocol("WM_DELETE_WINDOW", self.close_frame)

    def press_key_enter(self, event=None):
        self.crawl_gen_form()

    def select_all(self, event):
        # select all text
        event.widget.select_range(0, 'end')
        # move cursor to the end
        event.widget.icursor('end')

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
                        "請在" + const_define.TITLE + "目錄下使用UTF-16格式建立 " + filename, 'error')
            return ErrorType.FILE_ERROR.value

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
                        "請在" + const_define.TITLE + "目錄下使用UTF-16格式建立 " +filename, 'error')
            return ErrorType.FILE_ERROR.value

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

    def get_token(self):
        token = ''
        base_url = 'https://www.facebook.com'
        browser = RoboBrowser(history=True)
        try:
            browser.open(base_url)
        except:
            self.setlog("無法連接facebook, 請確認網路連線", "error")
            return

        form = browser.get_form(id='login_form')

        form["email"] = self.login_name_entry.get()
        form["pass"] = self.login_password_entry.get()
        # print(self.login_name_entry.get())
        # print(self.login_password_entry.get())
        browser.session.headers['Referer'] = base_url

        browser.submit_form(form)
        # print(str(browser.select))
        browser.open(const_define.FB_GRAPH_API_URL)

        content_lt = str(browser.select).splitlines()
        for line in content_lt:
            if line.find('},"props":{"accessToken":') > -1:
                re_h = re.match('.*accessToken":"(.*)","appID.*', line)
                if re_h:
                    token = re_h.group(1)

        # print(str(browser.select))
        return token

    def crawl_gen_form(self):
        # -----Clear text widge for log-----
        self.log_txt.config(state="normal")
        self.log_txt.delete('1.0', END)
        self.log_txt.config(state="disable")

        # -----get config ini file setting-----
        self.token_ini = self.read_config(SETTING_NAME, 'General', 'token')
        self.login_name_ini = self.read_config(SETTING_NAME, 'General', 'login_name')

        if self.token_ini == ErrorType.FILE_ERROR.value or self.login_name_ini == ErrorType.FILE_ERROR.value:
            tkinter.messagebox.showerror("Error",
                                         "錯誤! 讀取ini設定檔發生錯誤! "
                                         "請在" + const_define.TITLE + "目錄下使用UTF-16格式建立 " + SETTING_NAME)
            return

        # -----Get all fan page list-----
        fanpage_all_dic_ld = OrderedDict()
        file_fanpage_h = open(const_define.FANPAGE_NAME, encoding='utf8')
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
        file_fanpage_get_h = open(const_define.FANPAGE_GET_LIST, encoding='utf8')
        for fanpage_get_content in file_fanpage_get_h.readlines():
            fanpage_get_content = fanpage_get_content.strip('\n')
            # print(fanpage_get_content)
            if fanpage_get_content in fanpage_all_dic_ld.keys():
                # print(fanpage_all_dic_ld[fanpage_get_content])
                fanpage_dic_ld[fanpage_get_content] = fanpage_all_dic_ld[fanpage_get_content]
            else:
                self.setlog("粉絲頁: %s 不在資料庫中, 請確認%s與%s內容" % (fanpage_get_content, const_define.FANPAGE_NAME, const_define.FANPAGE_GET_LIST), "error")
                return
        file_fanpage_get_h.close()

        # -----Check user input token in GUI, auto get token if is empty-----
        self.user_input_token = self.token_entry.get()
        if self.user_input_token == "":
            self.setlog("自動抓取token中", "info")
            token = self.get_token()
            if token == '' or not token:
                tkinter.messagebox.showinfo("message", "自動取得token失敗, 請確認網路連線, 帳號密碼或手動輸入token", parent=self.top)
                return
            self.setlog("token: %s" % token, "info2")
        else:
            token = self.user_input_token

        # -----Store user input token, name and password into Setting.ini config file-----
        if not self.user_input_token == self.token_ini:
            self.setlog("新的token寫入設定檔: " + SETTING_NAME, "info")
            # print("path not match, write new path to ini")
            w_file_stat_lv = self.write_config(SETTING_NAME, 'General', 'token', self.user_input_token)

            if w_file_stat_lv == ErrorType.FILE_ERROR.value:
                tkinter.messagebox.showerror("Error",
                                             "錯誤! 寫入ini設定檔發生錯誤! "
                                             "請在" + const_define.TITLE + "目錄下使用UTF-16格式建立 "
                                             + SETTING_NAME, parent=self.top)
                return

        self.user_input_login_name = self.login_name_entry.get()
        if not self.user_input_login_name == self.login_name_ini:
            self.setlog("新的login name寫入設定檔: " + SETTING_NAME, "info")
            # print("path not match, write new path to ini")
            w_file_stat_lv = self.write_config(SETTING_NAME, 'General', 'login_name', self.user_input_login_name)

            if w_file_stat_lv == ErrorType.FILE_ERROR.value:
                tkinter.messagebox.showerror("Error",
                                             "錯誤! 寫入ini設定檔發生錯誤! "
                                             "請在" + const_define.TITLE + "目錄下使用UTF-16格式建立 "
                                             + SETTING_NAME, parent=self.top)
                return

        # ----create form sore folder-----
        form_foldername = re.sub(r":", '.', str(datetime.utcnow() + timedelta(hours=8)))

        # -----gen date time limt string-----
        # print(self.day_entry.get())
        mon = int(self.mon_entry.get())
        if mon and mon < 10:
                mon = str('0%d' % mon)
        day = str(int(self.day_entry.get()))
        datetime_limt = ('%s-%s-%s 00-00-00' % (self.year_entry.get(), mon, day))

        # -----start to crawl and gen form on other process-----
        # print(datetime_limt)
        # crawler.start_to_crawl_fanpage(self.user_input_token, fanpage_dic_ld, form_foldername, datetime_limt)
        q = Queue()
        process_lt = [crawler.start_to_crawl_fanpage]
        args_lt = [(token, fanpage_dic_ld, form_foldername, datetime_limt, q,)]

        process = Process(target=create_process, args=(process_lt, args_lt,))
        process.start()

        self.need_timer_restart = True
        self.print_log(q)

    def print_log(self, queue_h):
        # global timer
        try:
            log_ll = queue_h.get_nowait()
            log_type = log_ll[0]
            log_string = log_ll[1]
            if log_type != 'end':
                self.setlog(log_string, log_type)
            else:
                self.setlog(log_string, 'info')
        except:
            log_type = ''

        if log_type == 'end':
            self.need_timer_restart = False

        if self.need_timer_restart:
            self.timer_h = Timer(0.1, self.print_log, [queue_h])
            self.timer_h.start()


def check_all_file_status():
    if not os.path.exists(SETTING_NAME):
        return False
    if not os.path.exists('icons\\main.ico'):
        return False
    if not os.path.exists(const_define.FANPAGE_NAME):
        return False
    if not os.path.exists(const_define.FANPAGE_GET_LIST):
        return False
    return True


if __name__ == '__main__':
    # -----MessageBox will create tkinter, so create correct setting tkinter first
    root = Tk()
    root.title(const_define.TITLE)
    root.iconbitmap('icons\\main.ico')

    SETTING_NAME = "%s\\%s" % (os.getcwd(), const_define.SETTING_NAME)

    if not check_all_file_status():
        tkinter.messagebox.showerror("Error", "遺失必要檔案! \n\n請確認目錄有以下檔案存在, 或 "
                                              "重新安裝: " + const_define.TITLE + "\n"
                                              "1. " + SETTING_NAME + "\n"
                                              "2. " + const_define.FANPAGE_NAME + "\n"
                                              "3. " + const_define.FANPAGE_GET_LIST + "\n"
                                              "4. icons\\main.ico")
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
                                     "請確認檔案格式為UTF-8 (unicode format) 或重新安裝" + const_define.TITLE + "\n")
        sys.exit(0)

    # -----Start GUI class-----
    root.geometry('784x614')
    app = AJFanPageCrawl(master=root)
    # -----Start main loop-----
    app.mainloop()
