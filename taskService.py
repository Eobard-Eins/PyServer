import neo4j as nj
from untils import Nodes, Rels
def addTask(taskName:str, tags:list=[]):
    try:
        g=nj.Neo4j()
        g.newNode(Nodes.Task, taskName, {"status":1})
        for tag in tags:
            g.newRelationship(Nodes.Task, Nodes.Tag, taskName, tag, Rels.Own, taskName+"-"+tag, nj.getIDF(tag))
        return True
    except:
        return False 
    
def updateIDF():
    try:
        g=nj.Neo4j()
        g.updateIDF()
        return True
    except:
        return False

def disableTask(taskName:str):
    try:
        g=nj.Neo4j()
        g.setNodeInfo(taskName, Nodes.Task, {"status":0})
        return True
    except:
        return False
    
def getTasks(userName:str):
    try:
        g=nj.Neo4j()
        tasks = g.getRatings(userName)
        return tasks
    except:
        return []