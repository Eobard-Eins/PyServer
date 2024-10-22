import neo4j as nj
from untils import Nodes, Rels, Res, StatusCode
import jieba
def addTask(user:str,taskId:int,title:str,onLine:bool,latitude:float=91.0, longitude:float=181.0, tags:list=[])->Res:
    try:
        g=nj.Neo4j()
        # s=title+" "
        # for i in tags:
        #     s=s+"#"+i+" "
        g.newTask(user,taskId, title, latitude, longitude,tags)
        
        g.updateIDF()
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.error)

def disableTask(taskId:int):
    try:
        g=nj.Neo4j()
        g.setNodeInfo(Nodes.Task, taskId, {"status":0})
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.error)
    
def getTasks(userName:str,longitude:float,latitude:float, maxS:float, search:str, k:int):
    try:
        g=nj.Neo4j()
        rep=".*"
        if(search!=""):
            flag=True
            for i in jieba.cut_for_search(search):
                if flag:
                    rep=rep+i+".*"
                    flag=False
                else:
                    rep=rep+"|.*"+i+".*"
        
        tasks = g.getRatings(userName,longitude,latitude, maxS, rep, k)
        print("[INFO] get tasks:"+str(tasks))
        if(len(tasks)<k):
            t= g.getRatingsByRandom(userName,longitude,latitude, maxS, rep, k-len(tasks))
            tasks.extend(t)
        return Res.Success(tasks)
    except:
        return Res.Error(StatusCode.error)
    

def updatePrefer(userName:str,do:int,taskId:int)->Res:
    try:
        g=nj.Neo4j()
        alpha=1.0
        beta=0.0
        match do:
            case StatusCode.click:
                beta=0.2
            case StatusCode.like:
                beta=0.5
            case StatusCode.chat:
                beta=0.8
            case StatusCode.access:
                beta=0.8
            case StatusCode.dislike:
                beta=-0.5
        g.updatePrefer(user=userName,task=taskId,alpha=alpha,beta=beta)
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.error)
    
def addUser(user:str):
    try:
        g=nj.Neo4j()
        g.newNode(Nodes.User, user)
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.error)