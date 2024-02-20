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
        #print(sql)
        self.g.run(sql)

    def delRelationship(self,startType, relType, endType, startNode, relName, endNode):
        sql = "match (word:{0})-[r:{1}]->(n:{2}) where word.name='{3}' and r.name='{4}' and n.name='{5}' detach delete r".format(
            startType, relType, endType, startNode, relName, endNode)
        self.g.run(sql)

    def setNodeInfo(self,nodeType, nodeName, info={}):
        self.newNode(nodeType, nodeName, info)

    def delNode(self,nodeName, nodeType):
        sql = "match (p:{0}) where p.name='{1}' detach delete p".format(nodeType, nodeName)
        self.g.run(sql)
        
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
        sql='''
            match (n:Task)
            with count(n) as a
            match (n)-[o:Own]->(m:Tag) 
            with m,log(a/(count(n)+1)) as newValue
            match (tk:Task{status:1})-[k:Own]->(m)
            set k.value=newValue
            '''
        self.g.run(sql)
        print("IDF alread updated")
    
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
    
    def newTask(self,task:str,title:str,latitude:float,longitude:float,tags:list[str]):
        sql='''
            merge (newTk:Task {{name:"{0}"}})
            set newTk.status=1, newTk.search="{1}", newTk.latitude={2}, newTk.longitude={3}
            with {4} as tags, newTk
            foreach(tag in tags|
                merge(toTag:Tag {{name:tag}}) 
                merge (newTk)-[rel:Own{{name:newTk.name+"-"+tag}}]->(toTag) 
                set rel.value=1
            )
            '''.format(task, title, latitude, longitude, str(tags))
        print(sql)
        self.g.run(sql)


    
