import scrapy
import urllib
from urllib import parse
from ..items import CheckjiuyueItem
import logging
import xlrd
import os

class BaseBaiduSpider(scrapy.Spider):
    name = 'base'
    allowed_domains = ['baidu.com']
    start_urls = []
    domain = 'www.19lou.com'

    def start_requests(self):
        table = xlrd.open_workbook(os.path.join(os.path.dirname(os.path.dirname(__file__)),'data_origin.xlsx'))
        sheet = table.sheet_by_index(0)
        for r in range(1, sheet.nrows):
            novelname = sheet.cell(r, 0).value.strip()  # 小说名
            novelauthor = sheet.cell(r, 1).value.strip()  # 小说作者名
            # 填充baidu的url
            baidu_url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=site%3A{domain}%20{novelname}&oq=site%253A{domain}%2520wdasd&rsv_pq=eda862490000385c&rsv_t=b911lv5yefofX5GBinb7tTv5hkJpNwujbSamoPuujY03qLklDWgEgrZXI7A&rqlang=cn&rsv_enter=0&inputT=5594&rsv_sug3=220&rsv_sug2=0&rsv_sug4=7869'.format(
                novelname=urllib.parse.quote(novelname), domain=self.domain)  # quote方法处理url中文
            logging.debug(baidu_url)
            if len(novelauthor) == 0:  # 作者名为空，默认只按照小说名匹配。
                novelauthor = novelname  # 作者名和小说名赋相同值
            yield scrapy.Request(baidu_url, callback=self.parse,
                                 meta={'novelname': novelname, 'novelauthor': novelauthor})

    def parse(self, response):
        meta_parse_novelname = response.meta['novelname']
        meta_parse_novelauthor = response.meta['novelauthor']
        baidu_first_url = response.xpath('//*[@id="1"]/h3/a/@href').extract_first()  # 可能会搜不到东西
        logging.info(baidu_first_url)
        logging.debug(response.xpath("//title/text()").extract())
        if baidu_first_url != None:
            if len(baidu_first_url) > 0:
                yield scrapy.Request(url=baidu_first_url, callback=self.parse_detail,
                                     meta={'novelname': meta_parse_novelname,
                                           'novelauthor': meta_parse_novelauthor})  # 过去的url可能会搜到多种的，但是不和格式的取不到东西不处理
        else:
            pass

    def parse_detail(self, response):
        novelname = response.meta['novelname']
        novelauthor = response.meta['novelauthor']
        page_title = response.xpath("//title/text()").extract()
        title = title_str = None
        if page_title and len(page_title) > 0:
            title = title_str = page_title[0]

        logging.info(title_str)

        if title != None:
            if len(title) >= 0:  # 这个xpath下取不到title的是无效网页
                # 目标url
                aimurl = response.url
                item = CheckjiuyueItem()
                if not title_str:
                    title_str = 'title_str'
                if not aimurl:
                    aimurl = 'aimurl'
                if novelname in title_str:  # 此域名下面与名单疑似侵权作品 只匹配小说名的 作为参考
                    item["title"] = title_str
                    item["aimurl"] = aimurl
                    item["novelname"] = novelname
                    item["novelauthor"] = novelauthor
                    item["signal"] = 'reference'
                    logging.warning("仅通过小说名发现疑是侵权作品：%s, %s" % (title_str, aimurl))
                    yield item
                if novelname in title_str and novelauthor in title_str:  # 小说名，作者均重复 保存
                    item["title"] = title_str
                    item["aimurl"] = aimurl
                    item["novelname"] = novelname
                    item["novelauthor"] = novelauthor
                    item["signal"] = 'target'
                    logging.warning("通过小说名，作者 发现疑是侵权作品：%s, %s" % (title_str, aimurl))
                    yield item
        else:
            pass
