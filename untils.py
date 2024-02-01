# 工具包
#In[0]
import numpy as np
from numpy.linalg import norm
from neo4j import Nodes, Rels
import neo4j

#In[1]
def cos(a,b):
    #将向量a和b用0补齐到相同长度
    maxLen = max(len(a),len(b))
    a = np.pad(a,(0,maxLen-len(a)), 'constant')
    b = np.pad(b,(0,maxLen-len(b)), 'constant')

    return np.dot(a,b)/(norm(a)*norm(b))
