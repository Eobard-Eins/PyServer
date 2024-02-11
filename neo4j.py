import threading
from py2neo import Graph, Node, Relationship
import numpy as np
'''
@desc Ne04j 基础操作类；
采用图数据库原因：便于实现协同过滤/容易拓展
'''
#In[0]
class Neo4j:
    def __init__(self):
        self.g=Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            # http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j0",  # 数据库user name，如果没有更改过，应该是neo4j
            password="Server85426")

    def newNode(self, label, name, info={}):
        node = Node(label, name=name)# 节点name属性即ID
        for i in info:
            node[i] = info[i]
        self.g.create(node)
    def newRelationship(self, startType, endType, startNode, endNode, relType, relName, relValue):
        query=""
        if type(relValue) is str:
            query = "match(p:%s{ name:'%s'}) merge(q:%s {name:'%s'}) merge (p)-[rel:%s{name:'%s',value:'%s'}]->(q)" % (
            startType, startNode, endType, endNode, relType, relName, relValue)
        else:
            query = "match(p:%s{ name:'%s'}) merge(q:%s {name:'%s'}) merge (p)-[rel:%s{name:'%s',value:%s}]->(q)" % (
            startType, startNode, endType, endNode, relType, relName, relValue)
        self.g.run(query)

    def setRelationship(self, relType,relName,relInfo:map={}):
        sql=""
        for i in relInfo:
            if type(relInfo[i]) is str:
                sql = 'match ()-[p:{0}]->() where p.name="{1}" set p.{2}="{3}"'.format(relType, relName, i, relInfo[i])
            else:
                sql = 'match ()-[p:{0}]->() where p.name="{1}" set p.{2}={3}'.format(relType, relName, i, relInfo[i])
            #print(sql)
            self.g.run(sql)

    def getNode(self,node, nodeType):
        sql = "match (word:{0}) where word.name='{1}' return word".format(nodeType, node)
        dic = self.g.run(sql).data()[0]['word']
        return dict(dic)

    def getRelationNode(self,startNode, startType, endType, relName, relType):
        sql = "match (word:{0})-[r:{1}]->(n:{2}) where word.name='{3}' and r.name='{4}' return n.name".format(
            startType, relType, endType, startNode, relName)
        dict = self.g.run(sql).data()
        res = []
        for data in dict:
            res.append(data['n.name'])
        return res

    def delRelationship(self,startType, relType, endType, startNode, relName, endNode):
        sql = "match (word:{0})-[r:{1}]->(n:{2}) where word.name='{3}' and r.name='{4}' and n.name='{5}' detach delete r".format(
            startType, relType, endType, startNode, relName, endNode)
        self.g.run(sql)

    def setNodeInfo(self,nodeName, nodeType, info={}):
        for i in info:
            if type(info[i]) is str:
                #print(info[i])
                sql = 'match (p:{0}) where p.name="{1}" set p.{2}="{3}"'.format(nodeType, nodeName, i, info[i])
            else:
                sql='match (p:{0}) where p.name="{1}" set p.{2}={3}'.format(nodeType, nodeName, i, info[i])
            #print(sql)
            self.g.run(sql)

    def delNode(self,nodeName, nodeType):
        sql = "match (p:{0}) where p.name='{1}' detach delete p".format(nodeType, nodeName)
        self.g.run(sql)

    def getAllNode(self,nodeType,n:int=20):
        list = self.g.run("match (n:{0}) return n.name as name limit {1}".format(nodeType,n)).data()
        res = []
        for data in list:
            res.append(data['name'])
        return res

    def hasNode(self,nodeName, nodeType):
        res = self.g.run("match (n:{0}) where n.name='{1}' return n.name".format(nodeType, nodeName)).data()
        if len(res) == 0:
            return False
        else:
            return True
        
    def getRatings(self,userId:str,k:int=12):
        # 只有status为1的task才推荐
        sql="match (n:Task)-[a:Own]->(m:Tag)<-[b:Prefer]-(k:User) where k.name='{0}' and n.status=1 return n.name as taskId,sum(a.value*b.value) as value order by value desc limit {1}".format(userId,k)
        res= self.g.run(sql).data()
        return res


    def updateIDF(self):#更新IDF
        sql1="match (n:Task) return count(n) as a"#获取task总数
        sql2="match (n:Task)-[a:Own]->(m:Tag) return m.name as mn,count(n) as b"#获取拥有某个tag的task总数
        A=self.g.run(sql1).data()[0]['a']
        #print(A)
        b=self.g.run(sql2).data()
        threads=[]
        for i in b:
            thread=threading.Thread(target=Neo4j().updateIDFOnTag,args=(i['b'],i['mn'],A))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
            
        print("IDF alread updated")

    def updateIDFOnTag(self, num,tag,A):
        try:
            #name = threading.current_thread().getName()
            #print(f"线程{tag}开始执行，线程名称：{name}")
            k=np.log(A/(num+1))
            # 只有status为1的task才更新
            sql="match (n:Task)-[a:Own]->(m:Tag) where m.name='{0}' and n.status=1 set a.value={1}".format(tag,k)
            self.g.run(sql)
            #print(f"线程{tag}执行结束")
        except:
            print("线程{0}执行出错".format(tag))

    def getIDF(self,tag:str):
        sql1="match (n:Task) return count(n) as a"#获取task总数
        sql2="match (n:Task)-[a:Own]->(m:Tag) where m.name='{0}' return count(n) as b".format(tag)#获取拥有某个tag的task总数
        A=self.g.run(sql1).data()[0]['a']
        B=self.g.run(sql2).data()[0]['b']
        return np.log(A/(B+1))
        #print(A)

    def getUserPrefer(self,user:str,k:int=5):
        sql="match (u:User)-[p:Prefer]->(t:Tag) where u.name='{0}' return t.name as name,p.value as value order by p.value desc limit {1}".format(user,k)
        res=self.g.run(sql).data()
        return res
    
# #线程安全的neo4j操作类
# class ThreadSafeNeo4jExecutor:
#     def __init__(self):
#         self.g=Graph(
#             host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
#             # http_port=7474,  # neo4j 服务器监听的端口号
#             user="neo4j0",  # 数据库user name，如果没有更改过，应该是neo4j
#             password="Server85426")
#     def updateIDFOnTag(self, num,tag,A):
#         try:
#             #name = threading.current_thread().getName()
#             #print(f"线程{tag}开始执行，线程名称：{name}")
#             k=np.log(A/(num+1))
#             # 只有status为1的task才更新
#             sql="match (n:Task)-[a:Own]->(m:Tag) where m.name='{0}' and n.status=1 set a.value={1}".format(tag,k)
#             self.g.run(sql)
#             #print(f"线程{tag}执行结束")
#         except:
#             print("线程{0}执行出错".format(tag))