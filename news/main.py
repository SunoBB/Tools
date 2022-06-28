import re
import xml.etree.ElementTree as ET
import requests
import io
import os
from selenium import webdriver
import cv2
import config

class ShortNews():
    def __init__(self, group_code, group_file,source, type_news, url_rss, nb_post):
        chrome_options = webdriver.ChromeOptions()
        # prefs = {
        #     "profile.managed_default_content_settings.images": 2
        # }
        # chrome_options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome('./chromedriver', chrome_options=chrome_options)
        
        self.file_path_screen_shot = "screenshot.png"
        self.start_x, self.start_y, self.end_x, self.end_y = (
            15, 15, 600+15, 600+15)
        self.file_name_xml='text.xml'
        self.text_response=''

        self.group_code = group_code
        self.group_file = group_file
        self.source = source
        self.type_news = type_news
        self.url_rss = url_rss
        self.nb_post = nb_post
        self.file_path_html = '%s\index.html' % os.getcwd()
        self.file_path_html_show = '%s\index_show.html' % os.getcwd()
        #output
        self.list_title = ''
        self.list_link = ''
        self.list_description_text = ''
        
        

    def converHTML2png(self):
        
        self.driver.get(self.file_path_html_show)
        self.driver.get_screenshot_as_file(self.file_path_screen_shot)
        
    
    def cropImage(self,index):
        img_0 = cv2.imread(self.file_path_screen_shot)
        img_crop = img_0[self.start_y:self.end_y, self.start_x:self.end_x]
        #cv2.imwrite(self.file_path_screen_shot, img_crop)
        #print('%s_%s.png' % (self.group_code, index))
        cv2.imwrite('%s_%s.png' % (self.group_file, index), img_crop)

    def getTextResponse(self):
        res=requests.get(self.url_rss)
        self.text_response = res.text

    def writeFileXML(self):
        f = io.open(self.file_name_xml, 'w', encoding='utf-8')
        f.write(self.text_response)
        f.close()
    def parseXML(self):
        root = ET.parse(self.file_name_xml).getroot()
        list_title_xml=root.findall('channel/item/title')
        list_title = [title.text for title in list_title_xml]

        list_description_xml = root.findall('channel/item/description')
        list_description = [
            description.text for description in list_description_xml]
        list_description_text = [self.get_text_from_description(
            description) for description in list_description]

        list_link_xml = root.findall('channel/item/link')
        list_link = [
            link.text for link in list_link_xml]
        
        
        
        
        self.list_title = list_title
        self.list_description_text = list_description_text
        self.list_link = list_link
        


        
    def get_text_from_description(self, description):
        regex1 = re.search('<\/a>(.*)', description)
        return regex1.group(1)
    
    def get_first_img_of_post_new(self,link_post):
        try:
            res=requests.get(link_post)
            #bao tuoi tre
            if(self.group_code == 'tuoi_tre'):
                regex1 = re.search('<div><img src="(.*?)"', res.text)
                return regex1.group(1)
            return 'https://i.imgur.com/UvomB0q.jpg'
        except:
            return 'https://i.imgur.com/UvomB0q.jpg'

    def create_html_of_news(self,position):
        f = io.open(self.file_path_html, 'r', encoding='utf-8')
        ndung=f.read()
        f.close()
        
        ndung = ndung.replace(
            '{{url_img}}', self.get_first_img_of_post_new(self.list_link[position]))
        ndung = ndung.replace('{{typeNews}}', self.type_news)
        ndung = ndung.replace('{{source}}', self.source)
        ndung = ndung.replace('{{title}}', self.list_title[position])
        ndung = ndung.replace(
            '{{description}}', self.list_description_text[position])

        
        
        f2 = io.open(self.file_path_html_show, 'w', encoding='utf-8')
        f2.write(ndung)
        f2.close()
    
    
    def auto(self):
        self.getTextResponse()
        self.writeFileXML()
        self.parseXML()
        for i in range(self.nb_post):
            self.create_html_of_news(i)

            self.converHTML2png()
            self.cropImage(i)

        # self.driver.quit()


for e in config:
    #bot = ShortNews('tuoi_tre','Tuổi trẻ','Thể Thao','https://tuoitre.vn/rss/the-thao.rss',2)
    bot = ShortNews(e['group_code'], e['group_file'], e['source'],
                    e['typeNews'], e['link_rss'], e['nb_posts'])
    bot.auto()
    bot.driver.quit()

print('done')