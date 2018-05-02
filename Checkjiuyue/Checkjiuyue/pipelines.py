# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import time, datetime
from datetime import timedelta
import xlrd
from urllib import parse
import os
import shutil

date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
lasttime = datetime.date.today() + timedelta(days=-7)  # 上周的时间

'''域名要写全 whitelist.xlsx 白名单 data_origin要对比的数据 书名作者'''


class CheckjiuyuePipeline(object):
    urlset = set()

    def process_item(self, item, spider):
        if spider.name != None:
            flag = True
            table = xlrd.open_workbook('Checkjiuyue/Checkjiuyue/whitelist.xlsx')
            sheet = table.sheet_by_index(0)
            for r in range(1, sheet.nrows):
                whitelist_url = sheet.cell(r, 0).value.strip()  # 白名单中的每个url 一定要写全http格式
                white_domain = parse.urlparse(whitelist_url).netloc  # url域名
                if spider.domain in white_domain:
                    flag = False
            if not flag:  # flag为false说明域名在白名单中
                raise DropItem
            else:
                if item['signal'] == 'target':
                    with open('all_domains_files/target_%s_%s.txt' % (
                            spider.domain, date), 'a+') as f1:
                        title = '小说名：' + item['novelname'] + '  ' + '作者：' + item['novelauthor'] + ' >> ' + item[
                            "title"].replace('查看书签',
                                             '').replace(
                            '用道具', '').replace(
                            '_TXT下载', '').strip() + '\t'
                        aimurl = item["aimurl"] + '\n'
                        f1.write(title)
                        f1.write(aimurl)
                    return item
                if item['signal'] == 'reference':
                    with open('all_domains_files/reference_%s_%s.txt' % (
                            spider.domain, date), 'a+') as f2:
                        title = '小说名：' + item['novelname'] + '  ' + ' >> ' + item[
                            "title"].replace('查看书签',
                                             '').replace(
                            '用道具', '').replace(
                            '_TXT下载', '').strip() + '\t'
                        aimurl = item["aimurl"] + '\n'
                        f2.write(title)
                        f2.write(aimurl)
                    return item

    def close_spider(self, spider):
        open('all_domains_files/reference_%s_%s.txt' % (spider.domain, date), 'a')
        open('all_domains_files/target_%s_%s.txt' % (spider.domain, date), 'a')
        open('summary_files/summary_%s.txt' % date, 'a')
        if os.path.exists('all_domains_files/target_%s_%s.txt' % (
                spider.domain, lasttime)):  # 上次的文件存在
            with open('all_domains_files/target_%s_%s.txt' % (
                    spider.domain, lasttime), 'r')as f1:
                lst = f1.readlines()
            with open('all_domains_files/target_%s_%s.txt' % (
                    spider.domain, date),
                      'r')as f2:  # 今天文件
                tod = f2.readlines()
            with open('all_domains_files/add_%s_%s.txt' % (
                    spider.domain, date),
                      'w+')as f3:
                if len(tod) - len(lst) > 0:  # 今天新增
                    for arr in tod[len(lst):len(tod)]:
                        f3.write(arr)
        else:  # 昨天的文件如果没有就说明今天的内容全部新增
            shutil.copyfile('all_domains_files/target_%s_%s.txt' % (
                spider.domain, date), 'all_domains_files/add_%s_%s.txt' % (spider.domain, date))
        with open('summary_files/summary_%s.txt' % date, 'a+')as f:
            with open('all_domains_files/target_%s_%s.txt' % (spider.domain, date), 'r')as target:
                cont = target.readlines()
                if len(cont) > 0:
                    f.write('domain:%s下疑似侵权信息：' % spider.domain + '\n')
                    for i in cont:
                        f.write(i.strip() + '\n')