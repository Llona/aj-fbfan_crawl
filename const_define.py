from datetime import datetime, timedelta

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
