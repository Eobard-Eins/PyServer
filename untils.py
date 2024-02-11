# 工具包
#In[0]
import numpy as np
from numpy.linalg import norm
import neo4j

#In[1]
def cos(a,b):
    #将向量a和b用0补齐到相同长度
    maxLen = max(len(a),len(b))
    a = np.pad(a,(0,maxLen-len(a)), 'constant')
    b = np.pad(b,(0,maxLen-len(b)), 'constant')

    return np.dot(a,b)/(norm(a)*norm(b))


class Nodes:
    Task = "Task"#{name:id, status:0/1} status:0->不能推荐
    User = "User"
    Blog = "Blog"
    Tag = "Tag"

class Rels:
    Similarity = "Similarity"  # 相似度，user->task
    Recommended = "Recommended"  # 推荐过，user->task/blog
    Watched = "Watched"  # 看过,user->task/blog
    Rating = "Rating" # 评分，user->blog
    Own = "Own" #某个task或blog拥有tag属性  name:taskName-tageName
    Prefer="Prefer"#user对某tag的评分


