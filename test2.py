from dateutil.parser import parse
from datetime import datetime
import requests
import re
from robobrowser import RoboBrowser

FB_GRAPH_API_URL = r'https://developers.facebook.com/tools/explorer/'

email = ''
password = ''

def get_token():
    session = requests.session()
    response = session.post('https://www.facebook.com', data={
                            'lsd': 'lsd',
                            'charset_test': 'csettest',
                            'version': 'version',
                            'ajax': 'ajax',
                            'width': 'width',
                            'pxr': 'pxr',
                            'gps': 'gps',
                            'm_ts': 'mts',
                            'li': 'li',
                            'email': email,
                            'pass': password,
                             'login' : 'Log In'},
                            allow_redirects=False)

    #assert response.status_code == 302
    print(response.cookies)
    #assert 'c_user' in response.cookies
    cookies = response.cookies
    response = session.get(url=FB_GRAPH_API_URL,
                           headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Encoding': 'gzip',
                                    'Accept-Language': 'zh-TW'},
                           cookies=cookies,
                           allow_redirects=False,
                           verify=True)
    # print(response.text)
    file_write_h = open('test.txt', 'w', encoding='utf8')

    file_write_h.write(response.text)
    file_write_h.close()

def get_token2():
    base_url = 'https://www.facebook.com'
    browser = RoboBrowser(history=True)
    browser.open(base_url)

    form = browser.get_form(id='login_form')

    form["email"] = email
    form["pass"] = password
    browser.session.headers['Referer'] = base_url

    browser.submit_form(form)
    # print(str(browser.select))
    browser.open(FB_GRAPH_API_URL)

    file_write_h = open('test.txt', 'w', encoding='utf8')

    file_write_h.write(str(browser.select))
    file_write_h.close()
    # print(str(browser.select))


def get_token3():
    # file_read_h = open('test.txt', 'r', encoding='utf8')
    with open('test.txt', "r", encoding='utf8') as ins:
        for line in ins:
            if line.find('},"props":{"accessToken":') > -1:
                # re_h = re.match(r'"props":{"accessToken":"(.+)",', content)
                re_h = re.match('.*accessToken":"(.*)","appID.*', line)
                # fanpage_all_dic_ld[re_h.group(1)] = re_h.group(2)
                if re_h:
                    print(re_h.group(1))
get_token3()
