from dateutil.parser import parse
from datetime import datetime
import requests

token = '<access token>'
res = requests.get('https://graph.facebook.com/v2.3/me?access_token=%s'%(token))
print(res.text)


email = 'cwlkks@gmail.com'
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

