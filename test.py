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
a=time.perf_counter()
nj.updateIDF()
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")
# %% 获取推荐
import time
import neo4j as nj
a=time.perf_counter()
res=nj.getRatings("user1")
for i in res:
    print(i)
b=time.perf_counter()
print(f"程序运行时间为: {(b-a)*1000:.6f} ms")
# %% 添加用户评分
import neo4j as nj
import random
nn=1000
tags=set()
for i in range(500):
    k=random.randint(1,nn)
    tags.add("tag"+str(k))
print(tags.__len__)
for i in tags:
    nj.newRelationship(nj.Nodes.User, nj.Nodes.Tag, "user1", i, nj.Rels.Prefer,"user1-"+i, random.uniform(-5, 5))
# %%

