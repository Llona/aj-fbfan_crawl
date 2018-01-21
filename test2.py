from dateutil.parser import parse
from datetime import datetime
import requests

token = '<access token>'
res = requests.get('https://graph.facebook.com/v2.3/me?access_token=%s'%(token))
print(res.text)

