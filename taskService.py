import neo4j as nj
from untils import Nodes, Rels, Res, StatusCode
def addTask(taskName:str, tags:list=[])->Res:
    try:
        g=nj.Neo4j()
        g.newNode(Nodes.Task, taskName, {"status":1})
        for tag in tags:
            g.newRelationship(Nodes.Task, Nodes.Tag, taskName, tag, Rels.Own, taskName+"-"+tag, nj.getIDF(tag))
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
        g.setNodeInfo(taskName, Nodes.Task, {"status":0})
        return Res.Success(True)
    except:
        return Res.Error(StatusCode.neo4jError)
    
def getTasks(userName:str):
    try:
        g=nj.Neo4j()
        tasks = g.getRatings(userName)
        return Res.Success(tasks)
    except:
        return Res.Error(StatusCode.neo4jError)