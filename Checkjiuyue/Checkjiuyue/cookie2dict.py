from http.cookies import SimpleCookie

#浏览器中的原始cookies字符串
rawdata = '''BAIDUID=4CCC95BD0D5AABCCB0AAB6322510880B:FG=1; BIDUPSID=4CCC95BD0D5AABCCB0AAB6322510880B; PSTM=1513846213; H_PS_PSSID=1469_21110_17001_20930; PSINO=7'''

from http.cookies import SimpleCookie
cookie = SimpleCookie(rawdata)
cookies = {i.key:i.value for i in cookie.values()}
print(cookies)