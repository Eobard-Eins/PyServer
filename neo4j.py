import threading
from py2neo import Graph, Node, Relationship
import numpy as np
import jieba
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

    def newNode(self, label, name:str, info:dict={}):
        s=""            
        f=1
        for key,value in info.items():
            if f:
                s+="set "
                f=0
            else:
                s+=", "
            if type(value) is str:
                s=s+'n.%s="%s"'%(key,value)
            else:
                s=s+'n.%s=%s'%(key,value)
                
        sql='merge (n:%s { name:"%s"}) %s return count(n)'%(label,name,s)
        print(sql)
        self.g.run(sql)
    def newRelationship(self, startType, endType, startNode, endNode, relType, relName, relValue):
        query=""
        if type(relValue) is str:
            query = "match(p:%s{ name:'%s'}) merge(q:%s {name:'%s'}) merge (p)-[rel:%s{name:'%s'}]->(q) set rel.value='%s'" % (
            startType, startNode, endType, endNode, relType, relName, relValue)
        else:
            query = "match(p:%s{ name:'%s'}) merge(q:%s {name:'%s'}) merge (p)-[rel:%s{name:'%s'}]->(q) set rel.value=%s" % (
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

    def setNodeInfo(self,nodeType, nodeName, info={}):
        self.newNode(nodeType, nodeName, info)

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
        
    def getRatings(self, userId:str, longitude:float, latitude:float, s:float=41000.0, search:str=".*",k:int=12):
        # 只有status为1的task才推荐
        #Haversine公式计算距离
        sql='''
            match (n:Task{ status:1})-[a:Own]->(m:Tag)<-[b:Prefer]-(k:User{name:"%s"}) 
            with n,a,m,b,k,
                2 * 6371 * ASIN(
                    SQRT(
                    SIN((n.latitude - %s) * PI() / 360)^2 +
                    COS(%s * PI() / 180) *
                    COS(n.latitude * PI() / 180) *
                    SIN((n.longitude - %s) * PI() / 360)^2
                    )
                ) as distance,(n.latitude=91) as onLine
            where (onLine or distance<=%s)
              and n.search=~"%s"
              and not (k)-[:Recommended]->(n) 
            with n,k,sum(a.value*b.value) as value, distance, onLine
                order by value desc 
                limit %s
            merge (k)-[rec:Recommended{name:k.name+"-"+n.name}]->(n)
            return n.name as taskId, value, distance, onLine
            '''%(userId,latitude,latitude,longitude,s,search,k)
        #print(sql)
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
    
    def getIDFsOfTask(self,task:str):
        sql='match (n:Task)-[a:Own]->(t:Tag) where n.name="{0}" return t.name as name,a.value as value'.format(task)
        res=self.g.run(sql).data()
        return res
    def getPreferOfUserToTag(self,user:str,tag:str)->float:
        sql='match (u:User)-[a:Prefer]->(t:Tag) where u.name="{0}" and t.name="{1}" return a.value as value'.format(user,tag)
        res=self.g.run(sql).data()
        if len(res) == 0:
            return 0.0
        return res[0]['value']
    
    def updatePrefer(self,user:str,task:str,beta:float,alpha:float=1.0):
        sql='''match (u:User),(t:Tag)<-[b:Own]-(k:Task)
            where u.name="{0}" and k.name="{1}" 
            merge (u)-[a:Prefer{{name:u.name+"-"+t.name}}]->(t)
            on create set a.value={2}*b.value
            on match set a.value=case when a.value is null then {2}*b.value else {3}*a.value+{2}*b.value end
            return a'''.format(user,task,beta,alpha)
        #print(sql)
        res = self.g.run(sql).data()
        return res

    
