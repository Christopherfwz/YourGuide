# coding: utf-8

from django.core.wsgi import get_wsgi_application
from leancloud import Engine
from leancloud import LeanEngineError
import leancloud

import requests
import json

mainPage_engine = Engine(get_wsgi_application())


@mainPage_engine.define
def getBriefCityInfo(**params):
    weather_logo = {
        "晴": "https://cdn.heweather.com/cond_icon/100.png",
        "多云": "https://cdn.heweather.com/cond_icon/101.png",
        "少云": "https://cdn.heweather.com/cond_icon/102.png",
        "晴间多云": "https://cdn.heweather.com/cond_icon/103.png",
        "阴": "https://cdn.heweather.com/cond_icon/104.png",
        "有风": "https://cdn.heweather.com/cond_icon/200.png",
        "平静": "https://cdn.heweather.com/cond_icon/201.png",
        "微风": "https://cdn.heweather.com/cond_icon/202.png",
        "和风": "https://cdn.heweather.com/cond_icon/203.png",
        "清风": "https://cdn.heweather.com/cond_icon/204.png",
        "强风/劲风": "https://cdn.heweather.com/cond_icon/205.png",
        "疾风": "https://cdn.heweather.com/cond_icon/206.png",
        "大风": "https://cdn.heweather.com/cond_icon/207.png",
        "烈风": "https://cdn.heweather.com/cond_icon/208.png",
        "风暴": "https://cdn.heweather.com/cond_icon/209.png",
        "狂爆风": "https://cdn.heweather.com/cond_icon/210.png",
        "飓风": "https://cdn.heweather.com/cond_icon/211.png",
        "龙卷风": "https://cdn.heweather.com/cond_icon/212.png",
        "热带风暴": "https://cdn.heweather.com/cond_icon/213.png",
        "阵雨": "https://cdn.heweather.com/cond_icon/300.png",
        "强阵雨": "https://cdn.heweather.com/cond_icon/301.png",
        "雷阵雨": "https://cdn.heweather.com/cond_icon/302.png",
        "强雷阵雨": "https://cdn.heweather.com/cond_icon/303.png",
        "雷阵雨伴有冰雹": "https://cdn.heweather.com/cond_icon/304.png",
        "小雨": "https://cdn.heweather.com/cond_icon/305.png",
        "中雨": "https://cdn.heweather.com/cond_icon/306.png",
        "大雨": "https://cdn.heweather.com/cond_icon/307.png",
        "极端降雨": "https://cdn.heweather.com/cond_icon/308.png",
        "毛毛雨/细雨": "https://cdn.heweather.com/cond_icon/309.png",
        "暴雨": "https://cdn.heweather.com/cond_icon/310.png",
        "大暴雨": "https://cdn.heweather.com/cond_icon/311.png",
        "特大暴雨": "https://cdn.heweather.com/cond_icon/312.png",
        "冻雨": "https://cdn.heweather.com/cond_icon/313.png",
        "小到中雨": "https://cdn.heweather.com/cond_icon/314.png",
        "中到大雨": "https://cdn.heweather.com/cond_icon/315.png",
        "大到暴雨": "https://cdn.heweather.com/cond_icon/316.png",
        "暴雨到大暴雨": "https://cdn.heweather.com/cond_icon/317.png",
        "大暴雨到特大暴雨": "https://cdn.heweather.com/cond_icon/318.png",
        "雨": "https://cdn.heweather.com/cond_icon/399.png",
        "小雪": "https://cdn.heweather.com/cond_icon/400.png",
        "中雪": "https://cdn.heweather.com/cond_icon/401.png",
        "大雪": "https://cdn.heweather.com/cond_icon/402.png",
        "暴雪": "https://cdn.heweather.com/cond_icon/403.png",
        "雨夹雪": "https://cdn.heweather.com/cond_icon/404.png",
        "雨雪天气": "https://cdn.heweather.com/cond_icon/405.png",
        "阵雨夹雪": "https://cdn.heweather.com/cond_icon/406.png",
        "阵雪": "https://cdn.heweather.com/cond_icon/407.png",
        "小到中雪": "https://cdn.heweather.com/cond_icon/408.png",
        "中到大雪": "https://cdn.heweather.com/cond_icon/409.png",
        "大到暴雪": "https://cdn.heweather.com/cond_icon/410.png",
        "雪": "https://cdn.heweather.com/cond_icon/499.png",
        "薄雾": "https://cdn.heweather.com/cond_icon/500.png",
        "雾": "https://cdn.heweather.com/cond_icon/501.png",
        "霾": "https://cdn.heweather.com/cond_icon/502.png",
        "扬沙": "https://cdn.heweather.com/cond_icon/503.png",
        "浮尘": "https://cdn.heweather.com/cond_icon/504.png",
        "沙尘暴": "https://cdn.heweather.com/cond_icon/507.png",
        "强沙尘暴": "https://cdn.heweather.com/cond_icon/508.png",
        "浓雾": "https://cdn.heweather.com/cond_icon/509.png",
        "强浓雾": "https://cdn.heweather.com/cond_icon/510.png",
        "中度霾": "https://cdn.heweather.com/cond_icon/511.png",
        "重度霾": "https://cdn.heweather.com/cond_icon/512.png",
        "严重霾": "https://cdn.heweather.com/cond_icon/513.png",
        "大雾": "https://cdn.heweather.com/cond_icon/514.png",
        "特强浓雾": "https://cdn.heweather.com/cond_icon/515.png",
        "热": "https://cdn.heweather.com/cond_icon/900.png",
        "冷": "https://cdn.heweather.com/cond_icon/901.png",
        "未知": "https://cdn.heweather.com/cond_icon/999.png"
    }

    try:
        city = params['city']
    except:
        raise LeanEngineError(501, 'Invalid argument.')

    # # 天气logo地址(旧版天气api，目前只使用天气图片img_url)
    # from weather_id import getWeatherId
    # weather_id = getWeatherId(city=city)
    # if weather_id != -1:
    #     # url1 = "http://www.weather.com.cn/data/sk/" + weather_id + ".html"
    #     url2 = "http://www.weather.com.cn/data/cityinfo/" + weather_id + ".html"
    # else:
    #     return "No such city."
    # # r1 = requests.get(url1)
    # r2 = requests.get(url2)
    # # json_weather1 = json.loads(r1.content)
    # json_weather2 = json.loads(r2.content)
    # # temp = json_weather1["weatherinfo"]["temp"]
    # img1 = json_weather2["weatherinfo"]["img1"]
    # img_url = "http://m.weather.com.cn/img/b" + img1[1:]

    # 当前气温(新版天气api)
    tempurl = "https://www.sojson.com/open/api/weather/json.shtml?city=" + city
    r3 = requests.get(tempurl)
    json_weatherinfo = json.loads(r3.content)
    temp = json_weatherinfo["data"]["wendu"]
    weather_type = json_weatherinfo["data"]["forecast"][0]["type"]
    img_url = weather_logo.get(weather_type.encode("utf-8"))

    # 获得景点个数
    Attraction = leancloud.Object.extend('Attraction')
    query = Attraction.query
    query.equal_to("area", city)
    query_list = query.find()
    attraction_num = len(query_list)

    # 主页背景图url
    AreaPic = leancloud.Object.extend('AreaPic')
    query = AreaPic.query
    query.equal_to("area", city)
    query_list = query.find()
    if len(query_list) != 0:
        areaPicUrl = query_list[0].get("pic").url
    else:
        areaPicUrl = None

    # 去过的人数
    # TODO
    peopleBeenThereNum = 0

    # 照片数量
    # TODO
    photoNum = 0

    result = {"temperature": temp, "weather_logo": img_url, "sceneryNum": attraction_num, "background": areaPicUrl,
              "peopleNum": peopleBeenThereNum, "photoNum": photoNum}

    return result
