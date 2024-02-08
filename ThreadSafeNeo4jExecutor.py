import threading
import numpy as np
from py2neo import Graph, Node, Relationship

class ThreadSafeNeo4jExecutor:
    def __init__(self):
        self.g=Graph(
            host="127.0.0.1",  # neo4j 搭载服务器的ip地址，ifconfig可获取到
            # http_port=7474,  # neo4j 服务器监听的端口号
            user="neo4j0",  # 数据库user name，如果没有更改过，应该是neo4j
            password="Server85426")
    def updateIDFOnTag(self, num,tag,A):
        name = threading.current_thread().getName()
        print(f"线程{tag}开始执行，线程名称：{name}")
        k=np.log(A/(num+1))
        # 只有status为1的task才更新
        sql="match (n:Task)-[a:Own]->(m:Tag) where m.name='{0}' and n.status=1 set a.value={1}".format(tag,k)
        self.g.run(sql)
        print(f"线程{tag}执行结束")
