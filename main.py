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
@server.route('/test', methods=['post'])
def test():
    tn=flask.request.form['tasks'].split(',')
    print(type(tn))
    return json.dumps(tn)

#@desc 添加新委托 1
@server.route('/api/addNewTask', methods=['post'])
def addNewTask():
    tn=flask.request.form['task']
    tlt=flask.request.form['title']
    la=flask.request.form['latitude']
    lo=flask.request.form['longitude']
    ol=flask.request.form['onLine']
    tags=flask.request.form['tags'].split(',')
    if int(ol)==1:
        res=ts.addTask(tn, tlt, True, tags=tags)
    else:
        if len(la)==0 or len(lo)==0:
            return json.dumps(untils.Res.Error(untils.StatusCode.neo4jError).__dict__)
        res=ts.addTask(tn, tlt, False, float(la), float(lo), tags)
    return json.dumps(res.__dict__)

#@desc 禁用委托 1
@server.route('/api/disableTask', methods=['put'])
def disableTask():
    tn=flask.request.args.get('task')
    res=ts.disableTask(tn)
    return json.dumps(res.__dict__)

#@desc 获取推荐列表 1
@server.route('/api/getTasks', methods=['get'])
def getTasks():
    u=flask.request.form.get('user')
    s=flask.request.form.get('search')
    k=flask.request.form.get('k')
    longitude=flask.request.form.get('longitude')
    latitude=flask.request.form.get('latitude')
    maxS=flask.request.form.get('s')
    res=ts.getTasks(u,float(longitude),float(latitude),float(maxS),s,int(k))
    return json.dumps(res.__dict__)

#@desc 更新用户偏好 1
@server.route('/api/updatePrefer', methods=['put'])
def updatePrefer():
    u=flask.request.args.get('user')
    do=flask.request.args.get('do')
    tn=flask.request.args.get('task')
    res=ts.updatePrefer(u,int(do),tn)
    return json.dumps(res.__dict__)

#@desc 添加用户 1
@server.route('/api/addUser', methods=['post'])
def addUser():
    u=flask.request.args.get('user')
    res=ts.addUser(u)
    return json.dumps(res.__dict__)


server.run(host='127.0.0.1', port=8888, debug=False)