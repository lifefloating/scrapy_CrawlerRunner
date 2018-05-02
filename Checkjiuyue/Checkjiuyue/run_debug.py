from scrapy import cmdline

'''debug用'''
name = 'mamacn'
cmd = 'scrapy crawl {0}'.format(name)
cmdline.execute(cmd.split())