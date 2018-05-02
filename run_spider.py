import logging
import datetime, time
import os
from datetime import timedelta
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from Checkjiuyue.Checkjiuyue.dycls import get
from scrapy.settings import Settings
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import Header
import glob
import zipfile

date = time.strftime('%Y-%m-%d', time.localtime(time.time()))

checkfile = 'hasRunnedToday.txt'

settings = Settings({

    'SPIDER_MODULES': ['Checkjiuyue.Checkjiuyue.spiders'],

    'ROBOTSTXT_OBEY': False,
    'DEFAULT_REQUEST_HEADERS': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'},
    'ITEM_PIPELINES': {
        'Checkjiuyue.Checkjiuyue.pipelines.CheckjiuyuePipeline': 300, },

    'CONCURRENT_REQUESTS': 100,
    'DOWNLOAD_DELAY': 0.3

})


# 文件读入域名 创建spider
class check_run_spider():
    def run_all(self):
        hasRunnedToday = os.path.isfile(checkfile)
        if not hasRunnedToday:  # 今天此脚本未执行
            with open(checkfile, 'w+') as f:  # 执行前创建此文件
                pass
        else:
            os.remove(checkfile)
        with open('Checkjiuyue/Checkjiuyue/domain.txt', 'r')as f1:
            moudle_list = []
            for r in f1.readlines():
                name = r.replace('.', '').replace('\n', '').strip()  # name为domain去.
                domain = r.replace('\n', '').strip()
                with open('Checkjiuyue/Checkjiuyue/spiders/{}_spider.py'.format(name),
                          'w')as f:
                    f.write(
                        'from Checkjiuyue.Checkjiuyue.spiders.base_baidu_spider import BaseBaiduSpider' + '\n' + '\n')
                    f.write('class {}Spider(BaseBaiduSpider):'.format(name) + '\n')
                    f.write('\t' + "name='{}Spider'".format(name) + '\n')
                    f.write('\t' + "domain='{}'".format(domain) + '\n')
                moudle = get('Checkjiuyue.Checkjiuyue.spiders.{0}_spider.{1}Spider'.format(name, name))
                moudle_list.append(moudle)
        configure_logging()
        runner = CrawlerRunner(settings)
        for spider in moudle_list:
            runner.crawl(spider)
        d = runner.join()
        d.addBoth(lambda _: reactor.stop())
        reactor.run()
        self.send_email_zip_summary()
        time.sleep(self.getsleeptime())

    def send_email_zip_summary(self):
        # 邮箱smtp服务器
        host_server = 'smtp.126.com'
        # pwd为邮箱的授权码
        pwd = 'xxxxx'
        # 发件人的邮箱
        sender_mail = 'xxxxx'
        # 收件人邮箱
        receiver = 'xxxxx'  # 换成 sunliping@19lou.com
        # 邮件标题
        mail_title = '疑似侵权的小说名单 日期{}'.format(date)
        # 邮件正文内容
        msg = MIMEMultipart()
        # 邮件的正文内容
        mail_content = '说明：文件名 target文件为小说名，书名命中文件是结果文件，reference仅为小说名命中文件，作为参考，add是与上次比较新增内容；target为空说明没有疑似侵权信息' \
                       'zip为今日全部文件 summary_日期.txt是疑似侵权的汇总'
        msg["Subject"] = Header(mail_title, 'utf-8')
        msg["From"] = sender_mail
        msg["To"] = Header("whatever<{}>".format(receiver))

        # 邮件正文内容
        msg.attach(MIMEText(mail_content, 'html', 'utf-8'))

        # 构造附件1 压缩文件今日的全部文件
        today_files_list = glob.iglob('all_domains_files/*_*_{}.txt'.format(date))
        zipfile_today = zipfile.ZipFile('zip_{}.zip'.format(date), 'w')
        for today_files in today_files_list:
            zipfile_today.write(today_files)
        zipfile_today.close()
        att1 = MIMEApplication(open('zip_{}.zip'.format(date), 'rb').read())
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写
        att1["Content-Disposition"] = 'attachment; filename="zip_{}.zip"'.format(date)
        msg.attach(att1)
        # 构造附件2 summary 汇总文件
        att2 = MIMEText(open('summary_files/summary_{}.txt'.format(date), 'rb').read(), 'base64', 'utf-8')
        # att2 =MIMEText(open(os.path.join(os.getcwd(), 'Checkjiuyue/Checkjiuyue/summary_files','summary_{}.txt'.format(date)),'rb').read(),'base64','utf-8')
        att2["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写
        att2["Content-Disposition"] = 'attachment; filename="summary_%s.txt"' % date
        msg.attach(att2)
        # ssl登录
        smtp = SMTP_SSL(host_server)
        # 参数值为1表示开启调试模式，参数值为0关闭调试模式
        smtp.set_debuglevel(1)
        smtp.ehlo(host_server)
        smtp.login(sender_mail, pwd)
        smtp.sendmail(sender_mail, receiver, msg.as_string())
        print('send email to {} ok'.format(receiver))
        smtp.quit()

    def auto_run(self, d, h, m):
        '''d表示周几 h表示设定的小时，m为设定的分钟'''
        while True:
            # 判断是否达到设定时间
            while True:
                now = datetime.datetime.now()
                # 到达设定时间，结束内循环 执行run_all
                if now.weekday() == d and now.hour == h and now.minute == m:
                    if os.path.exists(checkfile):
                        os.remove(checkfile)
                    break
                # sleeptime之后再次检测
                time.sleep(self.getsleeptime())
            self.run_all()

    def getsleeptime(self):
        thistime = datetime.datetime.now()
        if thistime.weekday() < 3:  # 当前日期在周四之前
            str = (thistime + timedelta(7 + (3 - thistime.weekday()))).strftime('%Y-%m-%d') + ' 08:00:00'
        else:
            str = (thistime + timedelta(7 - (thistime.weekday() - 3))).strftime('%Y-%m-%d') + ' 08:00:00'
        nexttime = datetime.datetime.strptime(str, "%Y-%m-%d %H:%M:%S")
        logging.info(nexttime)  # 下次执行时间
        sleeptime = (nexttime - thistime).seconds  # sleep 秒数
        return sleeptime


if __name__ == '__main__':
    a = check_run_spider()
    a.auto_run(3, 8, 0)  # 周四8.0

