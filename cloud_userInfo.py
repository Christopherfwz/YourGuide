# coding: utf-8
# import datetime

import leancloud
import re
from django.core.wsgi import get_wsgi_application
from leancloud import Engine
from leancloud import LeanEngineError
import datetime

import requests
import json

cloud_userInfo = Engine(get_wsgi_application())


@cloud_userInfo.define
def getUserInfo(**params):
    try:
        id = params.get('id')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    # 查询author信息
    User = leancloud.Object.extend("_User")
    user = User.create_without_data(id)
    user.fetch()
    avatar = user.get("avatar")
    nickname = user.get("nickname")
    city = user.get("city")
    level = user.get("level")
    intro = user.get("introduction")
    is_guide = user.get("is_guide")

    if avatar:
        avatar_url = avatar.url
    else:
        avatar_url = None

    # 查询该用户的游记
    TravelNote = leancloud.Object.extend("TravelNote")
    query = TravelNote.query
    query.equal_to("author", user)
    query_list = query.find()
    moments = []
    for j in query_list:
        pics = []
        content = j.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # for url in picUrls_pre:
        #     print url
        #     c = re.compile('\]\(.*?\)', re.S)
        #     v = c.findall(url)[0]
        #     pics.append(v[2:-1])

        # 读取src中的url，放在pics里
        for group in picUrls_pre:
            match_obj = re.search('src="(.*?)"', group)
            picUrls = match_obj.groups()
            pics = list(picUrls)
        if len(pics) == 0:
            pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")
        # 查询author信息
        User = leancloud.Object.extend("_User")
        user = User.create_without_data(j.get("author").id)
        user.fetch()
        avatar = user.get("avatar")
        if avatar:
            avatar_url = avatar.url
        else:
            avatar_url = None

        # 查询comment数量
        Comment = leancloud.Object.extend("Comment")
        query = Comment.query
        query.equal_to("travelNote", j)
        query_list = query.find()
        commentNum = len(query_list)

        moments.append({
            "id": str(j.id),
            "image": pics[0],
            "title": j.get("title"),
            "nickname": user.get("username"),
            "avatar": avatar_url,
            "favNum": j.get("like"),
            "replyNum": commentNum,
            "price": j.get("spend"),
            "date": str(j.get("createdAt")),
        })

    favorites = []
    TravelNoteFav = leancloud.Object.extend("TravelNoteFav")
    query = TravelNoteFav.query
    query.equal_to("favUser", user)
    query_list = query.find()
    for j in query_list:
        pics = []
        travelNote = TravelNote.create_without_data(j.get("TravelNote").id)
        travelNote.fetch()

        content = travelNote.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # for url in picUrls_pre:
        #     print url
        #     c = re.compile('\]\(.*?\)', re.S)
        #     v = c.findall(url)[0]
        #     pics.append(v[2:-1])

        # 读取src中的url，放在pics里
        for group in picUrls_pre:
            match_obj = re.search('src="(.*?)"', group)
            picUrls = match_obj.groups()
            pics = list(picUrls)
        if len(pics) == 0:
            pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")
        # 查询author信息
        User = leancloud.Object.extend("_User")
        user = User.create_without_data(travelNote.get("author").id)
        user.fetch()
        avatar = user.get("avatar")
        if avatar:
            avatar_url = avatar.url
        else:
            avatar_url = None

        # 查询comment数量
        Comment = leancloud.Object.extend("Comment")
        query = Comment.query
        query.equal_to("travelNote", travelNote)
        query_list = query.find()
        commentNum = len(query_list)

        favorites.append({
            "id": str(travelNote.id),
            "image": pics[0],
            "title": travelNote.get("title"),
            "nickname": user.get("username"),
            "avatar": avatar_url,
            "favNum": travelNote.get("like"),
            "replyNum": commentNum,
            "price": travelNote.get("spend"),
            "date": str(travelNote.get("createdAt")),
        })

    result = {
        "avatar": avatar_url,
        "nickname": nickname,
        "city": city,
        "level": level,
        "intro": intro,
        "is_guide": is_guide,
        "moments": moments,
        "favorites": favorites,
    }

    return result


@cloud_userInfo.define
def getReceivedLike(**params):
    current_user = cloud_userInfo.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")

    try:
        page = params.get('page')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    array = []
    # 查询我的游记
    TravelNote = leancloud.Object.extend("TravelNote")
    query = TravelNote.query
    query.equal_to("author", current_user)
    query_list = query.find()
    # j是游记
    for j in query_list:
        # 这篇游记的图片、标题、发布时间
        title = j.get("title")
        publishTime = j.get("createdAt")

        pics = []
        content = j.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # for url in picUrls_pre:
        #     print url
        #     c = re.compile('\]\(.*?\)', re.S)
        #     v = c.findall(url)[0]
        #     pics.append(v[2:-1])

        # 读取src中的url，放在pics里
        for group in picUrls_pre:
            match_obj = re.search('src="(.*?)"', group)
            picUrls = match_obj.groups()
            pics = list(picUrls)
        if len(pics) == 0:
            pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")

        # 查询谁赞了这篇游记
        TravelNoteLike = leancloud.Object.extend("TravelNoteLike")
        query = TravelNoteLike.query
        query.equal_to("TravelNote", j)
        query_list1 = query.find()
        # k是赞了游记的记录
        for k in query_list1:
            # 查询author信息
            User = leancloud.Object.extend("_User")
            user = User.create_without_data(k.get("likeUser").id)
            user.fetch()
            avatar = user.get("avatar")
            if avatar:
                avatar_url = avatar.url
            else:
                avatar_url = None

            array.append({
                "id": str(k.id),  # 赞的id
                "image": pics[0],  # 你游记的图片，或者你评论的那个游记的图片，
                "title": title,  # 同上的那个游记的标题
                "nickname": user.get("username"),  # 赞的人的名字，
                "avatar": avatar_url,  # 赞的人的头像
                "time": k.get("createdAt").strftime("%Y-%m-%d %H:%M:%S"),  # 赞的时间
                "publishTime": publishTime.strftime("%Y-%m-%d %H:%M:%S"),  # 同上的那个游记的发布时间
                "type": 0,  # 0为赞了游记，1为赞了评论
                "comment": None
            })

    # 查询我的评论
    Comment = leancloud.Object.extend("Comment")
    query = Comment.query
    query.equal_to("comment_user", current_user)
    query_list = query.find()
    # j是评论
    for j in query_list:
        # 我的评论的内容
        content = j.get("content")
        # 我评论的游记
        travelNote = TravelNote.create_without_data(j.get("TravelNote").id)
        travelNote.fetch()

        # 这篇游记的图片、标题、发布时间
        title = travelNote.get("title")
        publishTime = travelNote.get("createdAt")

        pics = []
        content = travelNote.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # for url in picUrls_pre:
        #     print url
        #     c = re.compile('\]\(.*?\)', re.S)
        #     v = c.findall(url)[0]
        #     pics.append(v[2:-1])

        # 读取src中的url，放在pics里
        for group in picUrls_pre:
            match_obj = re.search('src="(.*?)"', group)
            picUrls = match_obj.groups()
            pics = list(picUrls)
        if len(pics) == 0:
            pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")

        # 查询谁赞了这个评论
        CommentLike = leancloud.Object.extend("CommentLike")
        query = CommentLike.query
        query.equal_to("comment", j)
        query_list1 = query.find()
        # k是赞了评论的记录
        for k in query_list1:
            # 查询author信息
            User = leancloud.Object.extend("_User")
            user = User.create_without_data(k.get("likeUser").id)
            user.fetch()
            avatar = user.get("avatar")
            if avatar:
                avatar_url = avatar.url
            else:
                avatar_url = None

            array.append({
                "id": str(k.id),  # 赞的id
                "image": pics[0],  # 你游记的图片，或者你评论的那个游记的图片，
                "title": title,  # 同上的那个游记的标题
                "nickname": user.get("username"),  # 赞的人的名字，
                "avatar": avatar_url,  # 赞的人的头像
                "time": k.get("createdAt").strftime("%Y-%m-%d %H:%M:%S"),  # 赞的时间
                "publishTime": publishTime.strftime("%Y-%m-%d %H:%M:%S"),  # 同上的那个游记的发布时间
                "type": 1,  # 0为赞了游记，1为赞了评论
                "comment": content
            })
    result = {
        "next": -1,
        "array": array,
    }

    return result


@cloud_userInfo.define
def getReceivedComment(**params):
    current_user = cloud_userInfo.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")

    try:
        page = params.get('page')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    array = []
    # 查询我的游记
    TravelNote = leancloud.Object.extend("TravelNote")
    query = TravelNote.query
    query.equal_to("author", current_user)
    query_list = query.find()
    # j是游记
    for j in query_list:
        # 这篇游记的图片、标题、发布时间
        title = j.get("title")
        publishTime = j.get("createdAt")

        pics = []
        content = j.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # for url in picUrls_pre:
        #     print url
        #     c = re.compile('\]\(.*?\)', re.S)
        #     v = c.findall(url)[0]
        #     pics.append(v[2:-1])

        # 读取src中的url，放在pics里
        for group in picUrls_pre:
            match_obj = re.search('src="(.*?)"', group)
            picUrls = match_obj.groups()
            pics = list(picUrls)
        if len(pics) == 0:
            pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")

        # 查询谁评论了这篇游记
        Comment = leancloud.Object.extend("Comment")
        query = Comment.query
        query.equal_to("TravelNote", j)
        query_list1 = query.find()
        # k是评论了游记的记录
        for k in query_list1:
            # 查询author信息
            User = leancloud.Object.extend("_User")
            user = User.create_without_data(k.get("comment_user").id)
            user.fetch()
            avatar = user.get("avatar")
            if avatar:
                avatar_url = avatar.url
            else:
                avatar_url = None

            array.append({
                "id": str(k.id),  # 评论的id
                "image": pics[0],  # 你游记的图片，或者你评论的那个游记的图片，
                "title": title,  # 同上的那个游记的标题
                "nickname": user.get("username"),  # 评论的人的名字，
                "avatar": avatar_url,  # 评论的人的头像
                "time": k.get("createdAt").strftime("%Y-%m-%d %H:%M:%S"),  # 评论的时间
                "publishTime": publishTime.strftime("%Y-%m-%d %H:%M:%S"),  # 同上的那个游记的发布时间
                "comment": k.get("content")
            })

    result = {
        "next": -1,
        "array": array,
    }

    return result


@cloud_userInfo.define
def getGuideInfo(**params):
    try:
        id = params.get('id')  # 用户id，是user的objectId，不是导游表的id
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    # 根据用户id查询用户
    User = leancloud.Object.extend("_User")
    user = User.create_without_data(id)
    user.fetch()
    # 根据用户查询导游信息
    Guide = leancloud.Object.extend("Guide")
    query = Guide.query
    query.equal_to("user", user)
    query_list = query.find()
    # i是导游
    for i in query_list:
        guide_id = i.id  # 导游id
        labels = []
        features = i.get("features")
        sightseeings = []
        about = i.get("about")

        # 根据导游id查询导游标签
        GuideNeedTagMap = leancloud.Object.extend("GuideNeedTagMap")
        query = GuideNeedTagMap.query
        query.equal_to("guide", i)
        query_list = query.find()

        # j是导游标签map的条目
        for j in query_list:
            GuideNeedTag = leancloud.Object.extend("GuideNeedTag")
            guideNeedTag = GuideNeedTag.create_without_data(j.get("guideNeedTag").id)
            guideNeedTag.fetch()
            labels.append(guideNeedTag.get("name"))

        # 根据导游id查询导游熟悉景点
        GuideAttractionMap = leancloud.Object.extend("GuideAttractionMap")
        query = GuideAttractionMap.query
        query.equal_to("guide", i)
        query_list = query.find()

        # j是导游熟悉景点map的条目
        for j in query_list:
            Attraction = leancloud.Object.extend("Attraction")
            attraction = Attraction.create_without_data(j.get("attraction").id)
            attraction.fetch()
            sightseeings.append(attraction.get("title"))

        # 查询该导游的相关游记
        TravelNote = leancloud.Object.extend("TravelNote")
        query = TravelNote.query
        query.equal_to("guide", i)
        query_list = query.find()
        travel_notes = []
        for j in query_list:
            pics = []
            content = j.get("content")
            if content != None:
                # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
                picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
            else:
                picUrls_pre = []
            # for url in picUrls_pre:
            #     print url
            #     c = re.compile('\]\(.*?\)', re.S)
            #     v = c.findall(url)[0]
            #     pics.append(v[2:-1])

            # 读取src中的url，放在pics里
            for group in picUrls_pre:
                match_obj = re.search('src="(.*?)"', group)
                picUrls = match_obj.groups()
                pics = list(picUrls)
            if len(pics) == 0:
                pics.append("http://lc-vqwqjioq.cn-n1.lcfile.com/72a3304b67086be0c5bd.jpg")
            # 查询author信息
            User = leancloud.Object.extend("_User")
            user = User.create_without_data(j.get("author").id)
            user.fetch()
            avatar = user.get("avatar")
            if avatar:
                avatar_url = avatar.url
            else:
                avatar_url = None

            # 查询comment数量
            Comment = leancloud.Object.extend("Comment")
            query = Comment.query
            query.equal_to("travelNote", j)
            query_list = query.find()
            commentNum = len(query_list)

            travel_notes.append({
                "id": str(j.id),
                "image": pics[0],
                "title": j.get("title"),
                "nickname": user.get("username"),
                "avatar": avatar_url,
                "favNum": j.get("like"),
                "replyNum": commentNum,
                "price": j.get("spend"),
                "date": [str(j.get("startDate")), str(j.get("endDate"))]
            })

        result = {
            "labels": labels,
            "features": features,
            "sightseeings": sightseeings,
            "about": about,
            "travel_notes": travel_notes
        }
        return result


@cloud_userInfo.define
def editUserInfo(**params):
    current_user = cloud_userInfo.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")

    try:
        filed = params.get('filed')
        data = params.get('data')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    try:
        current_user.set(filed, data)
        current_user.save()
    except:
        return {
            "status": -1,
            "message": '字段不存在或无权限修改',
        }

    return {
        "status": 0,
    }


@cloud_userInfo.define
def getFullInfo(**params):
    current_user = cloud_userInfo.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")
    phone = current_user.get("mobilePhoneNumber")
    nickname = current_user.get("nickname")
    introduction = current_user.get("introduction")
    user = {
        "phone": phone,
        "nickname": nickname,
        "introduction": introduction,
    }
    is_guide = current_user.get("is_guide")
    guide = {}
    # 根据用户查询导游信息
    Guide = leancloud.Object.extend("Guide")
    query = Guide.query
    query.equal_to("user", current_user)
    query_list = query.find()
    # i是导游
    for i in query_list:
        guide_id = i.id  # 导游id
        introduction = i.get("about")
        max_num = i.get("max_num")
        price = [i.get("price_low"), i.get("price_high")]
        city = i.get("area")
        sightseeings = []
        sightseeing_names = []
        features = i.get("features")

        # 根据导游id查询导游熟悉景点
        GuideAttractionMap = leancloud.Object.extend("GuideAttractionMap")
        query = GuideAttractionMap.query
        query.equal_to("guide", i)
        query_list = query.find()

        # j是导游熟悉景点map的条目
        for j in query_list:
            Attraction = leancloud.Object.extend("Attraction")
            attraction = Attraction.create_without_data(j.get("attraction").id)
            attraction.fetch()
            sightseeings.append(attraction.id)
            sightseeing_names.append(attraction.get("title"))

        guide = {
            "is_open": is_guide,
            "introduction": introduction,
            "max_num": max_num,
            "price": price,
            "city": city,
            "sightseeings": sightseeings,
            "sightseeing_names": sightseeing_names,
            "features": features
        }
        break

    result = {
        "user": user,
        "guide": guide
    }
    return result
