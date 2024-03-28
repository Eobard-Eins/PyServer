# 测试
#In[0]
import random
import taskService as ts
import time
# 记录当前时间
a=time.perf_counter()
res=ts.addTask("task2",["tag1","tag2"])
b=time.perf_counter()
print(res)
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")
# %%
import random
import taskService as ts
import time
import threading
taskNum=100000
tagNum=1000
threads=[]
def worker(i):
    name = threading.current_thread().getName()
    print(f"线程{i}开始执行，线程名称：{name}")
    
    n=random.randint(1,5)
    tags=[]
    for j in range(n):
        tags.append("tag"+str(random.randint(1,tagNum)))
    ts.addTask("task"+str(i),tags)
    print(f"线程{i}执行结束")
def test():
    
    cnt=0
    for i in range(int(100000),taskNum+1):
        thread=threading.Thread(target=worker,args=(i,))
        threads.append(thread)
        thread.start()
        cnt+=1
    for thread in threads:
        thread.join()
    print("success:"+str(cnt))
a=time.perf_counter()
test()
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")

# %% 更新IDF
import neo4j as nj
import time
a=time.perf_counter()
nj.Neo4j().updateIDF()
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")

# %% 获取推荐
import time
import neo4j as nj
a=time.perf_counter()
res=nj.Neo4j().getRatings("j0",121.47371,31.231556,10,k=1)
for i in res:
    print(i)
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")

# %% 添加用户评分
import neo4j as nj
import random
nn=1000
tags=set()
nj.Neo4j.newNode(nj.Nodes.User,"user1")
for i in range(500):
    k=random.randint(1,nn)
    tags.add("tag"+str(k))
print(len(tags))
for i in tags:
    nj.Neo4j.newRelationship(nj.Nodes.User, nj.Nodes.Tag, "user1", i, nj.Rels.Prefer,"user1-"+i, random.uniform(-5, 5))
print('done')

# %% 获取用户画像
import neo4j as nj
import time
a=time.perf_counter()
res=nj.Neo4j.getUserPrefer("user2")
print("user2用户画像：")
for i in res:
    print(i)
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")

# %% 测试推荐系统效果
import neo4j as nj
import taskService as ts
import random
import numpy as np
from untils import cos,Nodes,Rels
num=100
success=0
fail=0
for i in range(num):
    nn=1000
    tags=set()
    nj.Neo4j().newNode(Nodes.User,"user-test"+str(i))
    for j in range(500):
        k=random.randint(1,nn)
        tags.add("tag"+str(k))
    for j in tags:
        nj.Neo4j().newRelationship(Nodes.User, Nodes.Tag, "user-test"+str(i), j, Rels.Prefer,"user-test"+str(i)+"-"+j, random.uniform(-5, 5))
    print(str(i)+': 构建用户----done')

    up=nj.Neo4j().getUserPrefer("user-test"+str(i))
    tags=[]
    for j in up:
        tags.append(j['name'])
    print(str(i)+': 用户画像获取----done')

    ts.addTask("task-test"+str(i),tags)
    print(str(i)+': 目标task创建----done')

    sql1="match (n:Task) return count(n) as a"#获取task总数
    sql2="match (n:Task)-[a:Own]->(m:Tag) return m.name as mn,count(n) as b"#获取拥有某个tag的task总数
    A=nj.Neo4j().g.run(sql1).data()[0]['a']
    #print(A)
    b=nj.Neo4j().g.run(sql2).data()
    for j in b:
        k=np.log(A/(j['b']+1))
        # 只有status为1的task才更新
        sql="match (n:Task)-[a:Own]->(m:Tag) where m.name='{0}' and n.status=1 set a.value={1}".format(j['mn'],k)
        nj.Neo4j().g.run(sql)
    print(str(i)+': IDF更新----done')

    res=nj.Neo4j().getRatings("user-test"+str(i),1)
    print(str(i)+': 获取推荐----done')

    flag=False
    for j in res:
        if j['taskId']=="task-test"+str(i):
            flag=True
            break
    if flag:
        success+=1
    else:
        fail+=1
    print(str(i)+': finished,result:'+str(flag))
    print()

print("success:"+str(success))
print("fail:"+str(fail))
print("success rate:"+str(success/num))



# %%
import neo4j as nj
import time
import taskService as ts
# 记录当前时间
a=time.perf_counter()
ts.addTask("tkf","testNew",True,tags=["l1",'l2','l3'])
b=time.perf_counter()

print(f"程序运行时间为: {(b-a)*1000:.6f} ms")

# %%
import neo4j as nj
import time
import taskService as ts
from untils import cos,Nodes,Rels
res=ts.addTask("tkf","testNew",["l1",'l2','l3'])
print(res.__dict__)
# %%
sql='''
merge (newTk:Task {{name:"{0}"}})
set newTk.status=1, newTk.search="{1}", newTk.latitude={2}, newTk.longitude={3}
with {4} as tags, newTk
foreach(tag in tags|
    merge(toTag:Tag {{name:tag}}) 
    merge (newTk)-[rel:Own{{name:newTk.name+"-"+tag}}]->(toTag) 
    set rel.value=1
)
'''.format("tkf", "tkf", 11, 11, str(["l1",'l2','l3']))
print(sql)
# %%
import jieba
rep=".*"
flag=True
for i in jieba.cut_for_search("背景音乐"):
    if flag:
        rep=rep+i+".*"
        flag=False
    else:
        rep=rep+"|.*"+i+".*"

print(rep)
# %%
