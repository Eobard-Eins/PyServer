from jieba import analyse
import untils

A=[]
B=[]
text1 = "有湘大的同学还在学校吗？可以帮我去教务处盖章吗"
tags = analyse.extract_tags(text1, topK=20, withWeight=True, allowPOS=[])
for i in tags:
    A.append(i[1])
print(tags)
text2 = "有米哈游的同学还在公司吗？可以帮我画个设计图吗"
tags = analyse.extract_tags(text2, topK=20, withWeight=True, allowPOS=[])
for i in tags:
    B.append(i[1])

print(tags)

print(untils.cos(A,B))