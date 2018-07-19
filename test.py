# coding=utf-8
import types
from time import struct_time

import leancloud
import re
from leancloud import cloudfunc
import requests

leancloud.init("vqWQJiOQ0EX0Xtb7s3YaBIWr-gzGzoHsz", app_key="QtlXKEEEucDFKapMGlfFbNWy")
import datetime
import logging

logging.basicConfig(level=logging.DEBUG)

# print cloudfunc.run('getWeather', city='北京')
# user = leancloud.User()
# user.set_username('FengWenzhu1')
# user.set_password('123456')
# user.set_email('vipfwz1@gmail.com')
# user.sign_up()

user = leancloud.User()
user.login('FengWenZhu', '123456')
# user.follow("5aeef1d1ac502e607645d6b2")

# print user.id
# user.logout()
# print user.session_token

# TravelNote = leancloud.Object.extend('TravelNote')
# travelNote = TravelNote.create_without_data("5aef410ffe88c237402efedf")
# travelNote.fetch()
# TravelNotePic = leancloud.Object.extend('TravelNotePic')
# query1 = TravelNotePic.query
# query1.equal_to("travelNote",travelNote)
# query_list1 = query1.find()
# pics = []
# for j in query_list1:
#     pics.append(j.get("pic").url)
# print pics
# User = leancloud.Object.extend("_User")
# user= User.create_without_data(travelNote.get("author").id)
# user.fetch()
# print user.get("avatar")
# travelNote.set("author",user)
# travelNote.save()
# travelNote.set("title","hhhhhhhhh")
# travelNote.set("content","* Content")
# travelNote.set("area","武汉")
# travelNote.save()

# with open('/Users/user/Desktop/111.gif') as f:
#     avatar = leancloud.File('fileFromLocalFile', f)
#     avatar.save()
#     object_id = avatar.id

# TravelNotePic = leancloud.Object.extend('TravelNotePic')
# travelNotePic = TravelNotePic.create_without_data("5aef46109f54547470feaac2")
# travelNotePic.set("pic",avatar)
# travelNotePic.set("travelNote",travelNote)
# travelNotePic.save()

# Comment = leancloud.Object.extend('Comment')
# comment = Comment()
# comment.set("travelNote",travelNote)
# comment.set("comment_user",user)
# comment.set("content","gggggggggggggggggg")
# comment.set("thumbs",1000)
# comment.save()

# TravelNoteTag = leancloud.Object.extend('TravelNoteTag')
# travelNoteTag = TravelNoteTag()
# travelNoteTag.set("name","风景")
# travelNoteTag.save()
#
# TravelNoteTagMap = leancloud.Object.extend('TravelNoteTagMap')
# travelNoteTagMap = TravelNoteTagMap()
# travelNoteTagMap.set("travelNote",travelNote)
# travelNoteTagMap.set("travelNoteTag",travelNoteTag)
# travelNoteTagMap.save()
# Attraction = leancloud.Object.extend('Attraction')
# attraction = Attraction()
# attraction.set("area","武汉")
# attraction.set("name","黄鹤楼")
# attraction.save()

# GuideNeedTag = leancloud.Object.extend('GuideNeedTag')
# guideNeedTag = GuideNeedTag()
# guideNeedTag.set("name","女性")
# guideNeedTag.save()
#
# Guide = leancloud.Object.extend('Guide')
# guide = Guide()
# guide.set("user",user)
# guide.set("area","武汉")
# guide.set("price_low","100")
# guide.set("price_high","500")
# guide.set("is_professional",True)
# guide.set("score",5.0)
# guide.save()
#
# GuideAttractionMap = leancloud.Object.extend('GuideAttractionMap')
# guideAttractionMap = GuideAttractionMap()
# guideAttractionMap.set("guide",guide)
# guideAttractionMap.set("attraction",attraction)
# guideAttractionMap.save()
#
# GuideNeedTagMap = leancloud.Object.extend('GuideNeedTagMap')
# guideNeedTagMap = GuideNeedTagMap()
# guideNeedTagMap.set("guide",guide)
# guideNeedTagMap.set("guideNeedTag",guideNeedTag)
# guideNeedTagMap.save()
# keyword = "我"
# city = "武汉"
# category = "风景"
# TravelNoteTag = leancloud.Object.extend('TravelNoteTag')
# query = TravelNoteTag.query
# query.equal_to("name",category)
# query_list = query.find()
# TravelNoteTagMap = leancloud.Object.extend('TravelNoteTagMap')
# query = TravelNoteTagMap.query
# query.equal_to("travelNoteTag",query_list[0])
# query_list = query.find()
# for i in query_list:
#     TravelNote = leancloud.Object.extend('TravelNote')
#     query11 = TravelNote.query
#     a = query11.get(i.get("travelNote").id)
#     print "a", a.id, a.get("title")
# TravelNote = leancloud.Object.extend('TravelNote')
# Guide = leancloud.Object.extend('Guide')
# guide = Guide.create_without_data("5aef4af8ee920a1e147bdc14")
# guide.fetch()
# newTravelNote = TravelNote()
# newTravelNote.set("guide",guide)
# newTravelNote.set("author",user)
# newTravelNote.set("area","武汉")
# newTravelNote.set("peopleNum",1)
# newTravelNote.set("theme","玩耍")
# newTravelNote.set("path","床上->餐厅->床上")
# newTravelNote.set("startDate",datetime.datetime.strptime("2018-05-06 18:00:00", "%Y-%m-%d %H:%M:%S"))
# newTravelNote.set("endDate",datetime.datetime.strptime("2018-05-06 20:00:00","%Y-%m-%d %H:%M:%S"))
# newTravelNote.set("spend",10)
# newTravelNote.set("content","啊~嗯！")
# newTravelNote.save()
# print travel.id
# user.set("email","vipfwz2@gmail.com")
# user.save()

print cloudfunc.run('publishTravelNote', guideID='5aeef1d1ac502e607645d6b2',
                    target="zhengzhou",
                    peopleNum=10,
                    theme="SM",
                    path="暗黑功德箱-》更衣室-》B站",
                    startDate="2018-01-01 00:00:00",
                    endDate="2018-02-01 00:00:00",
                    spend=10,
                    content="Deep Dark Fantacy",
                    title="啊♂",
                    )
# TravelNote = leancloud.Object.extend("TravelNote")
# query = TravelNote.query
# query.equal_to("area","武汉")
# query_list = query.find()
# for i in query_list:
#     content = i.get("content")
#     if type(content)!=types.NoneType:
#         picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
#     else:
#         picUrls_pre = []
#     print picUrls_pre
