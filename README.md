# python服务类开发文档

> 2024/1/29
>- 记录：图数据库尽可能的少记录信息，比如task具体内容不存储，其应存于mysql中，返回spring推荐id列表，spring按列表查找信息

> 2024/2/1
>- 记录：使用TFIDF不太行，关键词提取不够准，词向量方案基本不行了。
>- 更正：用Tag，用户对不同tag有不同偏好权重，每个task对tag有不同权重，[基于标签的反向倒排索引做推荐](https://blog.csdn.net/LJY1806192339/article/details/124582942?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522170618978616800180657715%2522%252C%2522scm%2522%253A%252220140713.130102334.pc%255Fall.%2522%257D&request_id=170618978616800180657715&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~first_rank_ecpm_v1~rank_v31_ecpm-1-124582942-null-null.142^v99^pc_search_result_base7&utm_term=%E6%8E%A8%E8%8D%90%E7%AE%97%E6%B3%95%20%E5%9F%BA%E4%BA%8E%E5%9B%BE&spm=1018.2226.3001.4187)，其中，用户对tag的权重由其行为更正；对于多个类似tag不互通的问题，使用关键词提取不好解决，因为可能造成tag意思的偏移，但是可以将英文单词全部`转换为小写`，保证大小写造成不同tag。在前端输入tag时，可以推荐包含已输入词的tag供其选择，以减少同意不同词的发生。直接1用图数据库算会快一些。