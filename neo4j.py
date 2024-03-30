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

        sql=''
        if type(name) is str:
            sql='merge (n:%s { name:"%s"}) %s return count(n)'%(label,name,s)
        else:
            sql='merge (n:%s { name:%s}) %s return count(n)'%(label,name,s)
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
        sql0='''
            match (u:User{name:"%s"})-[:Prefer]->(t:Tag)
            return count(t) as flag
        '''%(userId)
        f=self.g.run(sql0).data()

        if f[0]['flag']==0:
            print("No Prefer")
            sql1='''
            match (n:Task{ status:1})
            with n,
                2 * 6371 * ASIN(
                    SQRT(
                    SIN((n.latitude - %s) * PI() / 360)^2 +
                    COS(%s * PI() / 180) *
                    COS(n.latitude * PI() / 180) *
                    SIN((n.longitude - %s) * PI() / 360)^2
                    )
                ) as distance,(n.latitude=91) as onLine
            match (k:User{name:"%s"})
            with n,k,distance,onLine
            match (tg:Tag)
            where (n.search=~"%s" or (tg.name=~"%s" and (tg)<-[:Own]-(n)))
              and (onLine or distance<=%s)
              and not (k)-[:Recommended]->(n) 

            with n,k,rand() as value, distance, onLine
            order by value desc 
            limit %s

            merge (k)-[rec:Recommended{name:k.name+"-"+n.name}]->(n)
            return n.name as taskId, value, distance, onLine
            '''%(latitude,latitude,longitude,userId,search,search,s,k)
            #print(sql1)
            res= self.g.run(sql1).data()
            return res
        
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
            
            match (tg:Tag)
            where (n.search=~"%s" or (tg.name=~"%s" and (tg)<-[:Own]-(n)))
              and (onLine or distance<=%s)
              and not (k)-[:Recommended]->(n) 

            with n,k,sum(a.value*b.value) as value, distance, onLine
                order by value desc 
                limit %s

            merge (k)-[rec:Recommended{name:k.name+"-"+n.name}]->(n)
            return n.name as taskId, value, distance, onLine
            '''%(userId,latitude,latitude,longitude,search,search,s,k)
        print(sql)
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
            
        #print("IDF alread updated")

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

    # def updateIDF(self):#更新IDF
    #     sql='''
    #         match (n:Task)
    #         with count(n) as a
    #         match (n)-[o:Own]->(m:Tag) 
    #         with m,log(a/(count(n)+1)) as newValue
    #         match (tk:Task{status:1})-[k:Own]->(m)
    #         set k.value=newValue
    #         '''
    #     self.g.run(sql)
    #     print("IDF alread updated")
    
    def updatePrefer(self,user:str,task:int,beta:float,alpha:float=1.0):
        sql='''match (u:User),(t:Tag)<-[b:Own]-(k:Task)
            where u.name="{0}" and k.name={1} 
            merge (u)-[a:Prefer{{name:u.name+"-"+t.name}}]->(t)
            on create set a.value={2}*b.value
            on match set a.value=case when a.value is null then {2}*b.value else {3}*a.value+{2}*b.value end
            return a'''.format(user,task,beta,alpha)
        #print(sql)
        res = self.g.run(sql).data()
        return res
    
    def newTask(self,user:str,task:int,search:str,latitude:float,longitude:float,tags:list[str]):
        sql='''
            merge (newTk:Task {{name:{0}}})
            set newTk.status=1, newTk.search="{1}", newTk.latitude={2}, newTk.longitude={3}
            with {4} as tags, newTk
            foreach(tag in tags|
                merge(toTag:Tag {{name:tag}}) 
                merge (newTk)-[rel:Own{{name:newTk.name+"-"+tag}}]->(toTag) 
                set rel.value=1
            )
            merge (u:User{{name:"{5}"}})-[:Recommended{name:newTk.name+"-"+newTk.name}]->(newTk)
            '''.format(task, search, latitude, longitude, str(tags),user)
        #print(sql)
        self.g.run(sql)


    
