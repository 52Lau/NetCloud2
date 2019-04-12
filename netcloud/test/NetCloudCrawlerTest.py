#!/usr/bin/env python3
# encoding: utf-8
"""
@version: 0.1
@author: lyrichu
@license: Apache Licence 
@contact: 919987476@qq.com
@site: http://www.github.com/Lyrichu
@file: NetCloudCrawlerTest.py
@time: 2019/01/06 00:18
@description:
test for NetCloudCrawler
"""
from netcloud.crawler import Crawler
from netcloud.util import Helper
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import base64
import requests
import json
import time
import os
import re
import sys

class NetCloudCrawlerTest:
    def __init__(self):
        self.input=sys.argv
        self.logger = Helper.get_logger()
        # self.singer_name = "刘瑞琪"
        # self.song_name = "离开的借口"
        self.singer_name = self.input[0]
        self.song_name = self.input[1]
        self.crawler = Crawler.NetCloudCrawler(self.song_name,self.singer_name)
        self.singer_url = 'http://music.163.com/artist?id={singer_id}'.format(singer_id=self.crawler.singer_id)

    def test_save_singer_all_hot_comments_to_file(self):
        hot_comments,song_path=self.crawler.save_singer_all_hot_comments_to_file()
        print(song_path)
        self.test_foreach_hot_comments(hot_comments,song_path)

    def test_get_singer_hot_songs_ids(self):
        self.logger.info(Helper.get_singer_hot_songs_ids(self.singer_url))

    def test_save_all_comments_to_file(self):
        self.crawler.save_all_comments_to_file()

    def test_threading_save_all_comments_to_file(self):
        self.crawler.save_all_comments_to_file_by_multi_threading()

    def test_get_lyrics(self):
        lyrics = self.crawler.get_lyrics_format_json()
        self.logger.info(lyrics)

    def test_save_lyrics_to_file(self):
        self.crawler.save_lyrics_to_file()

    def test_generate_all_necessary_files(self):
        self.crawler.generate_all_necessary_files()


    def test_foreach_hot_comments(self,hot_comments,song_path):
        for item in hot_comments:
            comment = item['content']  # comments content
            # replace comma to blank,because we want save text as csv format,
            # which is seperated by comma,so the commas in the text might cause confusions
            comment = comment.replace(",", " ").replace("\n", " ")
            likedCount = item['likedCount']  # the total agreements num
            comment_time = item['time']  # comment time(formatted in timestamp)
            userID = item['user']['userId']  # the commenter id
            nickname = item['user']['nickname']  # the nickname
            nickname = nickname.replace(",", " ")
            avatarUrl = item['user']['avatarUrl']
            # the comment info string
            comment_info = "{userID},{nickname},{avatarUrl},{comment_time},{likedCount},{comment}\n".format(
                userID=userID, nickname=nickname, avatarUrl=avatarUrl, comment_time=comment_time,likedCount=likedCount, comment=comment
            )

            path=song_path+ '\\' + avatarUrl.split("/")[-1]
            dirPath=song_path
            # path = 'D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\'+self.singer_name +'\\'+self.song_name+ '\\' + avatarUrl.split("/")[-1]
            # dirPath='D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\'+self.singer_name +'\\'+self.song_name
            # path = 'netcloud\\util\\songs\\' + self.singer_name + '\\' + self.song_name + '\\' + \avatarUrl.split("/")[-1]
            #dirPath = 'netcloud\\util\\songs\\' + self.singer_name + '\\' + self.song_name
            # 转换成localtime
            time_local = time.localtime(comment_time/1000)
            # 转换成新的时间格式(2016-05-05 20:28:54)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
            info = "@" + nickname + "\n\n" + dt + "\n\n在《" + self.song_name + "》下的评论"
            self.PictureSpider(avatarUrl,dirPath, path, info, comment)

    def test_get_hot_comments(self):
        hot_comments=self.crawler.get_hot_comments(self.crawler.comments_url)
        return hot_comments
        # for item in hot_comments:
        #     comment = item['content']  # comments content
        #     # replace comma to blank,because we want save text as csv format,
        #     # which is seperated by comma,so the commas in the text might cause confusions
        #     comment = comment.replace(",", " ").replace("\n", " ")
        #     likedCount = item['likedCount']  # the total agreements num
        #     comment_time = item['time']  # comment time(formatted in timestamp)
        #     userID = item['user']['userId']  # the commenter id
        #     nickname = item['user']['nickname']  # the nickname
        #     nickname = nickname.replace(",", " ")
        #     avatarUrl = item['user']['avatarUrl']
        #     # the comment info string
        #     comment_info = "{userID},{nickname},{avatarUrl},{comment_time},{likedCount},{comment}\n".format(
        #         userID=userID, nickname=nickname, avatarUrl=avatarUrl, comment_time=comment_time,likedCount=likedCount, comment=comment
        #     )
        #
        #     path = 'D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\'+self.singer_name +'\\'+self.song_name+ '\\' + avatarUrl.split("/")[-1]
        #     dirPath='D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\'+self.singer_name +'\\'+self.song_name
        #     # path = 'netcloud\\util\\songs\\' + self.singer_name + '\\' + self.song_name + '\\' + \avatarUrl.split("/")[-1]
        #     #dirPath = 'netcloud\\util\\songs\\' + self.singer_name + '\\' + self.song_name
        #     # 转换成localtime
        #     time_local = time.localtime(comment_time/1000)
        #     # 转换成新的时间格式(2016-05-05 20:28:54)
        #     dt = time.strftime("%Y-%m-%d %H:%M:%S", time_local)
        #     info = "@" + nickname + "\n\n" + dt + "\n\n在《" + self.song_name + "》下的评论"
        #     self.PictureSpider(avatarUrl,dirPath, path, info, comment)

    def PictureSpider(self, url, dirPath,path, info, text):
        '''
        下载评论者用户头像
        '''
        try:
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)
            # if not os.path.exists(path):

            else:
                r = requests.get(url)
                r.raise_for_status()
                # 使用with语句可以不用自己手动关闭已经打开的文件流
                with open(path, "wb+") as f:  # 开始写文件，wb代表写二进制文件
                    f.write(r.content)
                # 合成图片
                self.PictureCut(info, path, text)
                print("爬取完成")
                # print("文件已存在")
        except Exception as e:
            print("爬取失败:" + str(e))

    def PictureCut(self, info, Path, text):

        # 需要处理的图片路径 输覆盖原文件

        # 设置所使用的字体
        font = ImageFont.truetype("src/NetCloud/source/simsun.ttc", 26)
        font2 = ImageFont.truetype("src/NetCloud/source/simsun.ttc", 45)
        # 加载底图

        base_img = Image.open(u'D:\\Pyhton project\\NetCloud\\netcloud\\util\\source\\bg.jpg')
        # base_img = Image.open(u'D:\\Pyhton project\\NetCloud\\netcloud\\util\\source\\bg_2.jpg')
        # 可以查看图片的size和mode，常见mode有RGB和RGBA，RGBA比RGB多了Alpha透明度
        # print base_img.size, base_img.mode
        #box = (110, 140, 360, 400)  # 底图上需要P掉的区域  x轴 y轴 宽（减去x） 高（减去y）
        # 竖版
        box = (30, 330, 280, 590)  # 底图上需要P掉的区域  x轴 y轴 宽（减去x） 高（减去y）

        # 加载需要P上去的图片
        tmp_img = Image.open(u'' + Path)
        # 这里可以选择一块区域或者整张图片
        # region = tmp_img.crop((0,0,304,546)) #选择一块区域
        # 或者使用整张图片
        region = tmp_img

        # 使用 paste(region, box) 方法将图片粘贴到另一种图片上去.
        # 注意，region的大小必须和box的大小完全匹配。但是两张图片的mode可以不同，合并的时候回自动转化。如果需要保留透明度，则使用RGMA mode
        # 提前将图片进行缩放，以适应box区域大小
        # region = region.rotate(180) #对图片进行旋转
        region = region.resize((box[2] - box[0], box[3] - box[1]))
        base_img.paste(region, box)

        # 画图
        draw = ImageDraw.Draw(base_img)
        # 评论者信息
        # draw.text((120, 420), info, (255, 0, 0), font=font)  # 设置文字位置/内容/颜色/字体
        draw.text((50, 640), info, (255, 0, 0), font=font)  # 设置文字位置/内容/颜色/字体
        # 评论内容
        # text = '目前唯一支撑我活下去的就是我的父母了，想要让父母过得更好，不想结婚也不想交男朋友，深夜时总会一个人躺在床上胡思乱想，父母已经不年轻了，总有一天会先于我离开，真的到了那一天……我不知道我会不会跟着一起走，只希望，他们可以长命百岁，虽然不太可能，但是我自私的希望他们可以过得比我更久'
        textPur = ''
        # text='\t'+text
        while text:
            textPur = textPur + text[:10] + "\n"
            # print(text[:20])
            text = text[10:]
        draw.text((380, 350), textPur, (255, 0, 0), font=font2)  # 设置文字位置/内容/颜色/字体
        draw = ImageDraw.Draw(base_img)

        # base_img.show()  # 查看合成的图片
        # base_img.save('./out.png')  # 保存图片
        base_img.save(Path)  # 保存图片

    def test_all(self):
        '''
        运行全部test
        '''

        # self.test_get_hot_comments()
        self.test_save_singer_all_hot_comments_to_file()

        # self.test_get_singer_hot_songs_ids()
        #self.test_save_all_comments_to_file()
        # self.test_save_singer_all_hot_comments_to_file()
        # self.test_threading_save_all_comments_to_file()
        #self.test_generate_all_necessary_files()
        # self.PictureSpider('http://p2.music.126.net/jC9p7TpsxtItw9ODTl71nA==/109951163961587668.jpg',
        #                    'D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\刘瑞琪\\离开的借口',
        #                    'D:\\Pyhton project\\NetCloud\\netcloud\\util\\songs\\刘瑞琪\\离开的借口\\109951163961587668.jpg',
        #                    '@咬口奶油\n\n2019 - 01 - 11\n07: 59:48\n\n在《离开的借口》下的评论',
        #                    'packages是本项目包含哪些包,我这里只有一个名词为hive的包.'
        #                    )

if __name__ == '__main__':
    test = NetCloudCrawlerTest()
    test.test_all()

