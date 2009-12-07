from apachelogparser import *
from logparser_9949 import guest9949

s = '222.35.169.141 - - [07/Dec/2009:18:00:00 +0800] "POST /go.html?name=17173&u=http://www.17173.com/ HTTP/1.1" 200 50 "http://www.9949.cn/?uid=desktop" "Mozilla/4.0 (compatible; MSIE 6.0; IQ 0.9.8.1322; zh_cn; Windows NT 5.1))"'
regex = r'POST /go\.html\?name=(?P<name>.*?)&u=(?P<dest>http://.*?) HTTP'
parser = apachelog('', guest9949, regex)
g = parser.getGuestInfo(s)
print g.name.encode('gbk'), g.city.encode('GBK'), g.isp.encode('gbk')