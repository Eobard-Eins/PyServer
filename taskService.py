import neo4j as nj
from untils import Nodes, Rels, Res, StatusCode
import jieba
def addTask(taskName:str,title:str,onLine:bool,latitude:float=91.0, longitude:float=181.0, tags:list=[])->Res:
    try:
        g=nj.Neo4j()
        s=title+" "
        for i in tags:
            s=s+"#"+i+" "
        g.newTask(taskName, s, latitude, longitude,tags)
        g.updateIDF()
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)
    
def updateIDF():
    try:
        g=nj.Neo4j()
        g.updateIDF()
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)

def disableTask(taskName:str):
    try:
        g=nj.Neo4j()
        g.setNodeInfo(Nodes.Task, taskName, {"status":0})
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)
    
def getTasks(userName:str,longitude:float,latitude:float, maxS:float, search:str, k:int):
    try:
        g=nj.Neo4j()
        rep=".*"
        if(search!=""):
            flag=True
            for i in jieba.cut_for_search(search):
                if flag:
                    rep=res+".*"+i+".*"
                    flag=False
                else:
                    rep=rep+"|.*"+i+".*"
        else:
            print("search is empty")
        
        tasks = g.getRatings(userName,longitude,latitude, maxS, rep, k)

        return Res.Success(tasks)
    except:
        return Res.Error(StatusCode.neo4jError)
    

def updatePrefer(userName:str,do:int,taskName:str)->Res:
    '''
    do: 0->点击,1->点赞,2->联系,3->接取,4->不喜欢
    '''
    try:
        g=nj.Neo4j()
        alpha=1.0
        beta=0.0
        match do:
            case 0:
                beta=0.2
            case 1:
                beta=0.5
            case 2:
                beta=0.8
            case 3:
                beta=0.8
            case 4:
                beta=-0.5
        g.updatePrefer(user=userName,task=taskName,alpha=alpha,beta=beta)
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)
    
def markRecommend(user:str, tasks:list[str]):
    try:
        g=nj.Neo4j()
        for task in tasks:
            g.newRelationship(Nodes.User, Nodes.Task, user, task, Rels.Recommended, user+"-"+task, 1)
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)
    
def addUser(user:str):
    try:
        g=nj.Neo4j()
        g.newNode(Nodes.User, user)
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)