from py2neo import Graph, Node, Relationship

'''
@desc Ne04j 基础操作类；
采用图数据库原因：便于实现协同过滤/容易拓展
'''
#In[0]
g = Graph(
    host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
    # http_port=7474,  # neo4j 服务器监听的端口号
    user="neo4j0",  # 数据库user name，如果没有更改过，应该是neo4j
    password="Server85426")

def newNode(label, name, info={}):
    node = Node(label, name=name)# 节点name属性即ID
    for i in info:
        node[i] = info[i]
    g.create(node)
def newRelationship(startType, endType, startNode, endNode, relType, relName, relValue):
    query=""
    if type(relValue) is str:
        query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' merge (p)-[rel:%s{name:'%s',value:'%s'}]->(q)" % (
        startType, endType, startNode, endNode, relType, relName, relValue)
    else:
        query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' merge (p)-[rel:%s{name:'%s',value:%s}]->(q)" % (
        startType, endType, startNode, endNode, relType, relName, relValue)
    g.run(query)

def setRelationship(relType,relName,relInfo:map={}):
    sql=""
    for i in relInfo:
        if type(relInfo[i]) is str:
            sql = 'match (p:{0}) where p.name="{1}" set p.{2}="{3}"'.format(relType, relName, i, relInfo[i])
        else:
            sql = 'match (p:{0}) where p.name="{1}" set p.{2}={3}'.format(relType, relName, i, relInfo[i])
        g.run(sql)

def getNode(node, nodeType):
    sql = "match (word:{0}) where word.name='{1}' return word".format(nodeType, node)
    dic = g.run(sql).data()[0]['word']
    return dict(dic)

def getRelationNode(startNode, startType, endType, relName, relType):
    sql = "match (word:{0})-[r:{1}]->(n:{2}) where word.name='{3}' and r.name='{4}' return n.name".format(
        startType, relType, endType, startNode, relName)
    dict = g.run(sql).data()
    res = []
    for data in dict:
        res.append(data['n.name'])
    return res

def delRelationship(startType, relType, endType, startNode, relName, endNode):
    sql = "match (word:{0})-[r:{1}]->(n:{2}) where word.name='{3}' and r.name='{4}' and n.name='{5}' detach delete r".format(
        startType, relType, endType, startNode, relName, endNode)
    dict = g.run(sql)

def setNodeInfo(nodeName, nodeType, info={}):
    for i in info:
        if type(info[i]) is str:
            #print(info[i])
            sql = 'match (p:{0}) where p.name="{1}" set p.{2}="{3}"'.format(nodeType, nodeName, i, info[i])
        else:
            sql='match (p:{0}) where p.name="{1}" set p.{2}={3}'.format(nodeType, nodeName, i, info[i])
        #print(sql)
        g.run(sql)

def delNode(nodeName, nodeType):
    sql = "match (p:{0}) where p.name='{1}' detach delete p".format(nodeType, nodeName)
    g.run(sql)

def getAllNode(nodeType):
    list = g.run("match (n:{0}) return n.name as name".format(nodeType)).data()
    res = []
    for data in list:
        res.append(data['name'])
    return res

def hasNode(nodeName, nodeType):
    res = g.run("match (n:{0}) where n.name='{1}' return n.name".format(nodeType, nodeName)).data()
    if len(res) == 0:
        return False
    else:
        return True
    
def getRatings(userId:str):
    sql="match (n:Task)-[a:Own]->(m:Tag)<-[b:Prefer]-(k:User) where k.name='{0}' return n.name as taskId,sum(a.value*b.value) as value order by value desc".format(userId)
    res= g.run(sql).data()
    return res

# TODO:

class Nodes:
    Task = "Task"#{name:id,}
    User = "User"
    Blog = "Blog"
    Tag = "Tag"



class Rels:
    Similarity = "Similarity"  # 相似度，user->task
    Recommended = "Recommended"  # 推荐过，user->task/blog
    Watched = "Watched"  # 看过,user->task/blog
    Rating = "Rating" # 评分，user->blog
    Own = "Own" #某个task或blog拥有tag属性  name:taskName-tageName
    Prefer="Prefer"#user对某tag的评分



