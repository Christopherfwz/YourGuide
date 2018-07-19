# coding: utf-8
# import datetime
import types

import leancloud
import re
from django.core.wsgi import get_wsgi_application
from leancloud import Engine
from leancloud import LeanEngineError
import datetime

import requests
import json


travelNote_engine = Engine(get_wsgi_application())


@travelNote_engine.define
def getTravelNoteList(**params):
    try:
        city = params.get('city','')
        keyword = params.get('keyword','') # optional
        type = params.get('type', '')  # optional
        order_by = params.get('order_by', -1)  # optional
        category = params.get('category', '')  # optional
        page = params.get('page', -1)  # optional
        # # sightseeings = json.loads(params.get('sightseeings'))
        date = json.loads(params.get('date','null')) # optional
        spend = json.loads(params.get('spend','null')) # optional
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    # 计算当前季度月份区间
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    if 1 <= current_month <= 3:
        month_low = 1
        month_high = 3
    elif 4 <= current_month <= 6:
        month_low = 4
        month_high = 6
    elif 7 <= current_month <= 9:
        month_low = 7
        month_high = 9
    else:
        month_low = 9
        month_high = 12

    # 查询游记
    TravelNote = leancloud.Object.extend('TravelNote')
    if keyword == '':
        query = TravelNote.query
    else:
        query1 = TravelNote.query
        query2 = TravelNote.query
        query1.contains("title", keyword)
        query2.contains("content", keyword)
        query = leancloud.Query.or_(query1,query2)

    if city != '':
        query.equal_to("area", city)

    # 添加季度查询条件
    if type == 'season':
        query.greater_than_or_equal_to("createdAt", datetime.datetime(current_year, month_low, 1, 0, 0, 0))
        query.less_than("createdAt", datetime.datetime(current_year, month_high, 1, 0, 0, 0))
    # 添加精品条件(大于100的都是精品)
    elif type == 'boutique':
        query.greater_than_or_equal_to("like", 100)
    # 否则两个条件都不生效
    else:
        pass

    # order_by字段
    # 综合排序
    if order_by == 1:
        query.add_descending("createdAt")
    # 收藏多
    elif order_by == 2:
        query.add_descending("like")

    # 游记的日期范围，包含查询
    if date != None:
        query.greater_than_or_equal_to("createdAt", datetime.datetime.strptime(date[0], "%Y-%m-%d %H:%M:%S"))
        query.less_than("createdAt", datetime.datetime.strptime(date[1], "%Y-%m-%d %H:%M:%S"))

    # 开销， 两个int指范围，一个为-1时为不限，比如[-1, 100]指的是100元以下
    if spend != None:
        if spend[0] != -1:
            query.greater_than_or_equal_to("spend", spend[0])
        if spend[1] != -1:
            query.less_than_or_equal_to("spend", spend[1])

    # 开始查询
    query_list1 = query.find()

    # 根据category筛选
    result_list = []
    if category != '':
        TravelNoteTag = leancloud.Object.extend('TravelNoteTag')
        query = TravelNoteTag.query
        query.equal_to("name",category)
        query_list = query.find()
        TravelNoteTagMap = leancloud.Object.extend('TravelNoteTagMap')
        query = TravelNoteTagMap.query

        if len(query_list) != 0:
            query.equal_to("travelNoteTag",query_list[0])
            query_list = query.find()
        else:
            query_list = []

        for i in query_list:
            for j in query_list1:
                if j.id == i.get("travelNote").id:
                    query11 = TravelNote.query
                    a = query11.get(i.get("travelNote").id)
                    result_list.append(a)
                    break
        query_list1 = result_list

    array = []
    for i in query_list1:
        pics = []
        content = i.get("content")
        if content != None:
        # picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(i.get("content"))) #MD的正则表达式
            picUrls_pre = re.findall('<img.*?>', content)  # html的提取img标签的正则表达式
        else:
            picUrls_pre = []
        # else:
        #     picUrls_pre = []
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
        user = User.create_without_data(i.get("author").id)
        user.fetch()
        avatar = user.get("avatar")
        if avatar:
            avatar_url = avatar.url
        else:
            avatar_url = None

        # 查询comment数量
        Comment = leancloud.Object.extend("Comment")
        query = Comment.query
        query.equal_to("travelNote", i)
        query_list = query.find()
        commentNum = len(query_list)

        array.append({
            "id": str(i.id),
            "image": pics[0],
            "title": i.get("title"),
            "nickname": user.get("username"),
            "avatar": avatar_url,
            "favNum": i.get("like"),
            "replyNum": commentNum,
            "price": i.get("spend"),
            "date": str(i.get("createdAt")),
        })

    result = {
        "next": -1,
        "array": array
    }
    return result


@travelNote_engine.define
def getTravelNoteContent(**params):
    current_user = travelNote_engine.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")

    try:
        id = params.get('id')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    TravelNote = leancloud.Object.extend('TravelNote')
    travel = TravelNote.create_without_data(id)
    travel.fetch()

    # 查询是否收藏
    TravelNoteFav = leancloud.Object.extend('TravelNoteFav')
    query = TravelNoteFav.query
    query.equal_to("TravelNote",travel)
    query.equal_to("favUser",current_user)
    query_list = query.find()
    if len(query_list) <= 0:
        isFaved = False
    else:
        isFaved = True

    # 查询是否点赞
    TravelNoteLike = leancloud.Object.extend('TravelNoteLike')
    query = TravelNoteLike.query
    query.equal_to("TravelNote", travel)
    query.equal_to("likeUser", current_user)
    query_list = query.find()
    if len(query_list) <= 0:
        isLiked = False
    else:
        isLiked = True

    title = travel.get("title")
    content = travel.get("content")

    # 查询author信息
    User = leancloud.Object.extend("_User")
    user = User.create_without_data(travel.get("author").id)
    user.fetch()
    avatar = user.get("avatar")
    if avatar:
        avatar_url = avatar.url
    else:
        avatar_url = None
    authorid = travel.get("author").id
    nickname = user.get("nickname")
    avatar = avatar_url
    author = {
        "id": authorid,
        "nickname": nickname,
        "avatar": avatar,
    }

    # 查询行程信息
    date = (travel.get("startDate").strftime("%Y-%m-%d %H:%M:%S"),travel.get("endDate").strftime("%Y-%m-%d %H:%M:%S"))
    peopleNum = travel.get("peopleNum")
    theme = travel.get("theme")
    spend = travel.get("spend")
    path = travel.get("path")

    Guide = leancloud.Object.extend("Guide")
    guide1 = Guide.create_without_data(travel.get("guide").id)
    guide1.fetch()
    User = leancloud.Object.extend("_User")
    user1 = User.create_without_data(guide1.get("user").id)
    user1.fetch()

    guideName = user1.get("nickname")
    guide = user1.id
    journey = {
        "date": date,
        "peopleNum": peopleNum,
        "theme": theme,
        "spend": spend,
        "path": path,
        "guide": guide,
        "guideName": guideName,
    }

    # 查询comment数量
    Comment = leancloud.Object.extend("Comment")
    query = Comment.query
    query.equal_to("travelNote", travel)
    query_list = query.find()
    comments = []
    for i in query_list:
        User = leancloud.Object.extend("_User")
        user = User.create_without_data(i.get("comment_user").id)
        user.fetch()
        avatar = user.get("avatar")
        if avatar:
            avatar_url = avatar.url
        else:
            avatar_url = None
        authorid = user.id
        nickname = user.get("nickname")
        avatar = avatar_url

        # 查询评论是否被自己点赞
        CommentLike = leancloud.Object.extend('CommentLike')
        query = CommentLike.query
        query.equal_to("comment", i)
        query.equal_to("likeUser", current_user)
        query_list = query.find()
        if len(query_list) <= 0:
            isLiked = False
        else:
            isLiked = True

        comments.append({
            "id": i.id,
            "avatar": avatar,
            "nickname": nickname,
            "date": i.get("createAt"),
            "likeNum": i.get("thumbs"),
            "content": i.get("content"),
            "isLiked": isLiked
        })

    result = {
        "id" : id,
        "title": title,
        "content": content,
        "author": author,
        "isLiked": isLiked,
        "isFaved": isFaved,
        "journey": journey,
        "comments": comments,
    }
    return result


@travelNote_engine.define
def publishTravelNote(**params):
    try:
        guideID = params.get('guideID')
        target = params.get('target')
        peopleNum = params.get('peopleNum')
        theme = params.get('theme')
        path = params.get('path')
        startDate = params.get('startDate')
        endDate = params.get('endDate')
        spend = params.get('spend')
        content = params.get('content')
        title = params.get('title')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    try:
        current_user = travelNote_engine.current.user
        TravelNote = leancloud.Object.extend('TravelNote')

        User = leancloud.Object.extend("_User")
        # 这里是导游的用户id，不是导游id
        user = User.create_without_data(guideID)
        user.fetch()
        # 通过这个用户找到导游信息
        Guide = leancloud.Object.extend('Guide')
        query = Guide.query
        query.equal_to("user",user)
        query_list = query.find()
        if len(query_list) <= 0:
            return {
                "code": -1,
                "msg": "Failed. Please check if the guideid is valid or if the user is a guide."
            }
        guide = query_list[0]
        newTravelNote = TravelNote()
        newTravelNote.set("guide", guide)
        newTravelNote.set("author", current_user)
        newTravelNote.set("area", target)
        newTravelNote.set("peopleNum", peopleNum)
        newTravelNote.set("title", title)
        newTravelNote.set("theme", theme)
        newTravelNote.set("path", path)
        newTravelNote.set("startDate", datetime.datetime.strptime(startDate, "%Y-%m-%d %H:%M:%S"))
        newTravelNote.set("endDate", datetime.datetime.strptime(endDate, "%Y-%m-%d %H:%M:%S"))
        newTravelNote.set("spend", spend)
        newTravelNote.set("content", content)
        newTravelNote.save()

        return {
            "code": 0,
            "id": newTravelNote.id
        }
    except:
        return {
            "code": -1,
            "msg": "Failed. Please check if you have logged in"
        }


@travelNote_engine.define
def getTravelNoteFromFollowee(**params):
    current_user = travelNote_engine.current.user
    if not current_user:
        raise LeanEngineError("401", "Unauthorized")
    else:
        Followee = leancloud.Object.extend('_Followee')
        query = Followee.query
        query.equal_to("user", current_user)
        query_list = query.find()
        result = []
        array = []
        # i = Followee
        for i in query_list:
            TravelNote = leancloud.Object.extend('TravelNote')
            query1 = TravelNote.query
            User = leancloud.Object.extend("_User")
            user = User.create_without_data(i.get("followee").id)
            user.fetch()
            query1.equal_to("author", user)
            query_list1 = query1.find()
            # j = TravelNote from i

            for j in query_list1:
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

                array.append({
                    "id": str(j.id),
                    "image": pics[0],
                    "title": j.get("title"),
                    "nickname": user.get("nickname"),
                    "avatar": avatar_url,
                    "favNum": j.get("like"),
                    "replyNum": commentNum,
                    "price": j.get("spend"),
                    "date": str(j.get("createdAt")),
                })

        result = {
            "next": -1,
            "array": array
        }
        return result

@travelNote_engine.define
def likeTravelNote(**params):
    try:
        id = params.get('id')
        like = params.get('like')
    except:
        raise LeanEngineError(501, 'Invalid argument.')
    current_user = travelNote_engine.current.user
    TravelNote = leancloud.Object.extend("TravelNote")
    travelNote = TravelNote.create_without_data(id)
    travelNote.fetch()
    TravelNoteLike = leancloud.Object.extend("TravelNoteLike")
    if like == 'true':
        travelNoteLike = TravelNoteLike()
        travelNoteLike.set("TravelNote",travelNote)
        travelNoteLike.set("likeUser",current_user)
        travelNoteLike.save()
    elif like == 'false':
        travelNoteLike = TravelNoteLike()
        query = TravelNoteLike.query
        query.equal_to("TravelNote", travelNote)
        query.equal_to("likeUser", current_user)
        query_list = query.find()
        for i in query_list:
            i.destroy()
    else:
        return {
            "status": -1,
            "messgae": "请求非法",
        }

    return {
        "status": 0,
    }


@travelNote_engine.define
def favTravelNote(**params):
    try:
        id = params.get('id')
        like = params.get('like')
    except:
        raise LeanEngineError(501, 'Invalid argument.')
    current_user = travelNote_engine.current.user
    TravelNote = leancloud.Object.extend("TravelNote")
    travelNote = TravelNote.create_without_data(id)
    travelNote.fetch()
    TravelNoteFav = leancloud.Object.extend("TravelNoteFav")
    if like == 'true':
        travelNoteFav = TravelNoteFav()
        travelNoteFav.set("TravelNote",travelNote)
        travelNoteFav.set("favUser",current_user)
        travelNoteFav.save()
    elif like == 'false':
        travelNoteFav = TravelNoteFav()
        query = TravelNoteFav.query
        query.equal_to("TravelNote", travelNote)
        query.equal_to("favUser", current_user)
        query_list = query.find()
        for i in query_list:
            i.destroy()
    else:
        return {
            "status": -1,
            "messgae": "请求非法",
        }

    return {
        "status": 0,
    }

@travelNote_engine.define
def commentTravelNote(**params):
    try:
        id = params.get('id')
        content = params.get('content')
    except:
        raise LeanEngineError(501, 'Invalid argument.')
    current_user = travelNote_engine.current.user
    TravelNote = leancloud.Object.extend("TravelNote")
    travelNote = TravelNote.create_without_data(id)
    travelNote.fetch()
    Comment = leancloud.Object.extend("Comment")
    comment = Comment()
    comment.set("TravelNote",travelNote)
    comment.set("comment_user",current_user)
    comment.set("content",content)
    comment.save()

    return {
        "status": 0,
    }

@travelNote_engine.define
def likeComment(**params):
    try:
        id = params.get('id')
        like = params.get('like')
    except:
        raise LeanEngineError(501, 'Invalid argument.')
    current_user = travelNote_engine.current.user
    Comment = leancloud.Object.extend("Comment")
    comment = Comment.create_without_data(id)
    comment.fetch()
    CommentLike = leancloud.Object.extend("CommentLike")
    if like == 'true':
        commentLike = CommentLike()
        commentLike.set("comment",comment)
        commentLike.set("likeUser",current_user)
        commentLike.save()
    elif like == 'false':
        commentLike = CommentLike()
        query = CommentLike.query
        query.equal_to("comment", comment)
        query.equal_to("likeUser", current_user)
        query_list = query.find()
        for i in query_list:
            i.destroy()
    else:
        return {
            "status": -1,
            "messgae": "请求非法",
        }

    return {
        "status": 0,
    }

@travelNote_engine.define
def getAttraction(**params):
    try:
        city = params.get('city')
        page = params.get('page',0)
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    array = []
    Attraction = leancloud.Object.extend("Attraction")
    query = Attraction.query
    query.equal_to("area", city)
    query_list = query.find()
    for i in query_list:
        array.append({
            "id": i.id,
            "title": i.get("title"),
            "price": i.get("price"),
            "recommend_num": i.get("recommend_num"),
            "image": i.get("image"),
            "travel_note_num": i.get("travel_note_num"),
        })
    result = {
        "next": -1,
        "array": array,
    }
    return result

@travelNote_engine.define
def searchAttraction(**params):
    try:
        keyword = params.get('keyword')
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    array = []
    Attraction = leancloud.Object.extend("Attraction")
    query = Attraction.query
    query.contains("title", keyword)
    query_list = query.find()
    for i in query_list:
        array.append({
            "id": i.id,
            "name": i.get("title"),
            # "price": i.get("price"),
            # "recommend_num": i.get("recommend_num"),
            "image": i.get("image"),
            "city": i.get("area"),
            # "travel_note_num": i.get("travel_note_num"),
        })
    result = {
        "array": array,
    }
    return result



# @travelNote_engine.define
# def getTravelNoteByTag(**params):
#     try:
#         tagName = params['tag']
#     except:
#         raise LeanEngineError(501, 'Invalid argument.')
#     TravelNoteTag = leancloud.Object.extend('TravelNoteTag')
#     query0 = TravelNoteTag.query
#     query0.equal_to('name', tagName)
#     query_list0 = query0.find()
#     if len(query_list0) >= 1:
#         travelNoteTag = query_list0[0]
#     else:
#         raise LeanEngineError(501, 'No such tag.')
#     TravelNoteTagMap = leancloud.Object.extend('TravelNoteTagMap')
#     query = TravelNoteTagMap.query
#     query.equal_to("travelNoteTag", travelNoteTag)
#     query.limit(10)
#     query.add_descending("createdAt")
#     query_list = query.find()
#     result = []
#     for i in query_list:
#         TravelNote = leancloud.Object.extend('TravelNote')
#         travelNote = TravelNote.create_without_data(i.get("travelNote").id)
#         travelNote.fetch()
#
#         pics = []
#         picUrls_pre = re.findall('!\[.*?\]\(.*?\)', str(travelNote.get("content")))
#         for url in picUrls_pre:
#             print url
#             c = re.compile('\]\(.*?\)', re.S)
#             v = c.findall(url)[0]
#             pics.append(v[2:-1])
#         User = leancloud.Object.extend("_User")
#         user = User.create_without_data(travelNote.get("author").id)
#         user.fetch()
#         avatar = user.get("avatar")
#         if avatar:
#             avatar_url = avatar.url
#         else:
#             avatar_url = None
#         result.append({"summary": str(travelNote.get("content"))[:20], "place": travelNote.get("area"),
#                        "time": str(travelNote.get("createdAt")), "id": travelNote.id, "pics": pics,
#                        "title": travelNote.get("title"), "author_avatar": avatar_url,
#                        "author_name": user.get("username"), "watched": travelNote.get("watched"),
#                        "like": travelNote.get("like")})
#     return result






# @travelNote_engine.define
# def getTravelNoteDetail(**params):
#     try:
#         travelNoteId = params['travelNoteId']
#     except:
#         raise LeanEngineError(501, 'Invalid argument.')
#     current_user = travelNote_engine.current.user
#     if not current_user:
#         raise LeanEngineError(401, "Unauthorized")
#     else:
#         TravelNote = leancloud.Object.extend('TravelNote')
#         travelNote = TravelNote.create_without_data(travelNoteId)
#         travelNote.fetch()
#         if not travelNote:
#             raise LeanEngineError(501, 'Invalid travelNoteId.')
#
#         Comment = leancloud.Object.extend('Comment')
#         query = Comment.query
#         query.equal_to("travelNote", travelNote)
#         query.add_descending("createdAt")
#         query_list = query.find()
#
#         comments = []
#         for i in query_list:
#             User = leancloud.Object.extend("_User")
#             user = User.create_without_data(i.get("comment_user").id)
#             user.fetch()
#             avatar = user.get("avatar")
#             if avatar:
#                 avatar_url = avatar.url
#             else:
#                 avatar_url = None
#             comments.append(
#                 {
#                     "commentId": i.id,
#                     "content": i.get("content"),
#                     "avatorUrl": avatar_url,
#                     "commmenterName": user.get("username"),
#                     "thumbs": i.get("thumbs"),
#                     "time": str(i.get("createdAt"))
#                 }
#             )
#
#         User = leancloud.Object.extend("_User")
#         user = User.create_without_data(travelNote.get("author").id)
#         user.fetch()
#         avatar = user.get("avatar")
#         if avatar:
#             author_avatar_url = avatar.url
#         else:
#             author_avatar_url = None
#
#         result = {
#             "authorId": user.id,
#             "authorAvatorUrl": author_avatar_url,
#             "authorName": user.get("username"),
#             "content": travelNote.get("content"),
#             "title": travelNote.get("title"),
#             "area": travelNote.get("area"),
#             "time": str(travelNote.get("createdAt")),
#             "watched": travelNote.get("watched"),
#             "like": travelNote.get("like"),
#             "comment": comments
#         }
#     return result
