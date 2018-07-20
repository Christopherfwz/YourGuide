# coding: utf-8

from django.core.wsgi import get_wsgi_application
from leancloud import Engine
from leancloud import LeanEngineError
from cloud_mainPage import mainPage_engine
from cloud_travelNote import travelNote_engine
from cloud_userInfo import cloud_userInfo
from datetime import datetime

engine = Engine(get_wsgi_application())
engine.register(mainPage_engine)
engine.register(travelNote_engine)
engine.register(cloud_userInfo)

@engine.define
def hello(**params):
    if 'name' in params:
        return 'Hello, {}!'.format(params['name'])
    else:
        return 'Hello, LeanCloud!'

@engine.define
def date(**params):
    return {
        "date": datetime.now()
    }

@engine.before_save('Todo')
def before_todo_save(todo):
    content = todo.get('content')
    if not content:
        raise LeanEngineError('内容不能为空')
    if len(content) >= 240:
        todo.set('content', content[:240] + ' ...')

