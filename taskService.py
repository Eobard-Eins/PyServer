import neo4j as nj
from neo4j import Nodes, Rels
def addTask(taskName:str, tags:list=[]):
    try:
        nj.newNode(Nodes.Task, taskName, {"status":1})
        for tag in tags:
            nj.newRelationship(Nodes.Task, Nodes.Tag, taskName, tag, Rels.Own, taskName+"-"+tag, nj.getIDF(tag))
        return True
    except:
        return False 
    
