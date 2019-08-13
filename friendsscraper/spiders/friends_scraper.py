import scrapy
import string
import csv
import re
import os.path

from scrapy.selector import Selector
from scrapy.http import HtmlResponse


class ScriptsSpider(scrapy.Spider):
    name = "friends"

    start_urls = ['https://fangj.github.io/friends/']


    def parse(self, response):
        eps = response.css('li a::attr(href)').extract() 

        # Season 7 includes an outtakes episode; remove it

        eps.remove('season/07outtakes.html')

        for ep in eps:   
            yield scrapy.Request(response.urljoin(ep), callback=self.parse_script)
                   

    def parse_script(self, response):
        
        # Extract episode title and number 

        title = response.css('title::text').getall()
        num_url = re.sub(r'[^0-9]', '', response.url)

        if len(num_url) > 4:
            if num_url[0] == '0':
                ep_num = num_url[1:4]
            else:
                ep_num = num_url[:4]
        else:
            if num_url[0] == '0':
                ep_num = num_url[1:]
            else:
                ep_num = num_url

        # Season 9 has some irregularities that need to be dealt with manually

        if ep_num == '906':
            title = response.css('h1::text').getall()
        elif ep_num == '909':
            title = response.css('h2::text').getall()
        elif ep_num == '912':
            title = response.css('font::text').getall()

        if len(title) >= 1 and ep_num != '909':
            title = title[0]
        elif len(title) >= 1 and ep_num == '909':
            title = title[1]
        elif len(title) == 0 or title == None:
            title = "TITLE NOT FOUND"

        title = re.sub(r'', "'", title)
        title = re.sub(r"[^a-zA-Z' ]", '', title)
        title = re.sub('Crazy For Friends', '', title)
        title = re.sub('^Friends ', '', title)
        title = re.sub(' Script$', '', title)

        if ep_num == '906':
            title = re.sub('th episode', '', title)
        elif ep_num == '911':
            title = re.sub('FRIENDS', '', title)
        elif ep_num == '912':
            title = re.sub('TOW', 'the one with', title)

        title = title.strip().lower()


        # Double Episodes:      212-213 The Superbowl
        #                       615-616 That Could Have Been
        #                       923-924 In Barbados
        #                       1017-1018 Last One

        if ep_num == '911':
            rawlines = response.css('html *::text').getall()
        elif ep_num == '915':
            rawlines = response.css('body *::text').getall()
        else:
            rawlines = response.css('p *::text').getall()

        
            
        filename = 'script-titles.csv'

        if os.path.exists(filename):
            with open(filename, 'a') as f:
                newFileWriter = csv.writer(f)
                newFileWriter.writerow([response.url, title, ep_num])
        else:
            with open(filename, 'w') as f:
                newFileWriter = csv.writer(f)
                newFileWriter.writerow(['url', 'ep_title', 'ep_num'])
                newFileWriter.writerow([response.url, title, ep_num])
            
        
        with open('ep-%s.csv' % ep_num, 'a', encoding='utf-8') as f:
            newFileWriter = csv.writer(f)
            newFileWriter.writerow([title])
            for i in rawlines:
                newFileWriter.writerow([i])

            #newFileWriter.writerow(([response.url], response.css('h1::text').getall()[-1]))



        #page = response.url.split("/")[-2]
        
        #filename = 'scripts-%s.html' % page
        #with open(filename, 'wb') as f:
            #f.write(response.body)

            # for href in response.css('a::attr(href)').extract():
            #   resp = scrapy.Request(response.urljoin(href), self.parse)
            #   print(resp)
            #   filename = start_urls[0] + href
            #   with open(filename, 'wb') as f:
            #       f.write(resp.body)
