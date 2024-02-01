# 测试
#In[0]
import numpy as np
from numpy.linalg import norm
from neo4j import Nodes, Rels
import neo4j

#In[1]
res=neo4j.getRatings("user1")
print(res)

#In[2]
neo4j.newNode(Nodes.Task, "task1")
neo4j.newNode(Nodes.Task, "task2")
neo4j.newNode(Nodes.Task, "task3")


neo4j.newNode(Nodes.User, "user1")


neo4j.newNode(Nodes.Tag, "tag1", )
neo4j.newNode(Nodes.Tag, "tag2", )
neo4j.newNode(Nodes.Tag, "tag3", )
neo4j.newNode(Nodes.Tag, "tag4", )
neo4j.newNode(Nodes.Tag, "tag5", )


neo4j.newRelationship(Nodes.User, Nodes.Tag, "user1", "tag1", Rels.Prefer, "user1-tag1", 0.0114)
neo4j.newRelationship(Nodes.User, Nodes.Tag, "user1", "tag2", Rels.Prefer, "user1-tag2", 0.186)
neo4j.newRelationship(Nodes.User, Nodes.Tag, "user1", "tag3", Rels.Prefer, "user1-tag3", 0.4601)
neo4j.newRelationship(Nodes.User, Nodes.Tag, "user1", "tag4", Rels.Prefer, "user1-tag4", 0.106)
neo4j.newRelationship(Nodes.User, Nodes.Tag, "user1", "tag5", Rels.Prefer, "user1-tag5", 0.597)


neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task1", "tag1", Rels.Own, "task1-tag1", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task1", "tag2", Rels.Own, "task1-tag2", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task1", "tag3", Rels.Own, "task1-tag3", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task1", "tag4", Rels.Own, "task1-tag4", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task1", "tag5", Rels.Own, "task1-tag5", 1)

neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task2", "tag1", Rels.Own, "task1-tag1", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task2", "tag3", Rels.Own, "task1-tag3", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task2", "tag4", Rels.Own, "task1-tag4", 1)

neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task3", "tag1", Rels.Own, "task3-tag1", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task3", "tag3", Rels.Own, "task3-tag3", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task3", "tag4", Rels.Own, "task3-tag4", 1)
neo4j.newRelationship(Nodes.Task, Nodes.Tag, "task3", "tag5", Rels.Own, "task3-tag5", 1)

#In[3]
res=neo4j.getNode("task1", Nodes.Task)
print(res)
# In[4]
res=neo4j.getAllNode(Nodes.Task)
print(res)

# %%
