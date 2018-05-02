# scrapy_CrawlerRunner
主要记录下动态加载模块和类，scrapy多爬虫运行，scrapy外部加载settings
可参考https://blog.csdn.net/qq_33775402/article/details/63835978
## 注意点
  主要记录下动态加载模块和类，scrapy多爬虫运行，scrapy外部加载settings 基本都在run_spiders.py 
### 百度搜索
  按照百度搜索出结果，第一条匹配度应该是最高的，只抓第一条作为对比

  抓site:域名 小说名的结果页面 小说名这里是中文 在URL里面被处理成utf-8的URL编码 用urllib.quote处理编码
  改下useragent 改成Baiduspider/2.0什么的，不然会抓不到数据
### 详细页面
  虽然Baidu搜索结果页，并不直接显示这个网页的真实url，但是发现scrapy会帮你重定向到他的真实url
  到那里直接response.url就可以取到真实url
  取标题作者，作为对比依据
