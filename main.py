import untils
from py2neo import Graph
import flask
import json
import taskService as ts
'''
@desc: api接口
'''
server = flask.Flask(__name__)

## 启动命令：neo4j.bat console

#@desc 添加新委托，生成特征向量并计算与各用户的相似度
@server.route('/task/addNewTask', methods=['post'])
def addNewTask():
    
    res=ts.addTask()
    return 'Hello World'

#@desc 删除委托
@server.route('/task/disableTask', methods=['delete'])
def disableTask():
    return 'Hello World'

#@desc 获取推荐列表
@server.route('/task/getTasks', methods=['get'])
def getTasks():
    return 'Hello World'

#@desc 标记task为看过
@server.route('/task/addWatched', methods=['post','put'])
def addWatched():
    return 'Hello World'



#@desc 添加新博客
@server.route('/blog/addNewBlog', methods=['post'])
def addNewBlog():
    return 'Hello World'

#@desc 删除博客
@server.route('/blog/delNewBlog', methods=['delete'])
def delNewBlog():
    return 'Hello World'

#@desc 修改对某博客的评分
@server.route('/blog/updateRating', methods=['put','post'])
def updateRating():
    return 'Hello World'

#@desc 获取博客推荐列表
@server.route('/blog/getBlogs', methods=['get'])
def getBlogs():
    return 'Hello World'