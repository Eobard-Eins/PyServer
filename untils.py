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
    Tag = "Tag"

class Rels:
    Recommended = "Recommended"  # 推荐过，user->task/blog
    Own = "Own" #某个task或blog拥有tag属性  name:taskName-tageName
    Prefer="Prefer"#user对某tag的评分
    


class StatusCode:
    success = 1000  # 成功
    successButUserNotExist = 1001  # 成功登录但是用户不存在

    # 手机号、验证码、密码相关错误码
    phoneFormatError = 1100  # 手机号格式错误
    passwordFormatError = 1101  # 密码格式错误
    passwordError = 1102  # 密码错误
    captchaError = 1103  # 验证码错误
    passwordInconsistent = 1104  # 密码不一致
    setPasswordError = 1105  # 通信数据库设置密码错误

    # 用户信息相关错误码
    userNotExist = 1200  # 用户不存在
    userExist = 1201  # 用户已存在
    setUsernameError = 1202  # 通信数据库设置用户名时出现错误
    setLongitudeAndLatitudeError = 1203  # 通信数据库设置经纬度时出现错误
    setPointError = 1204  # 通信数据库设置积分时出现错误
    setRegisteredError = 1204  # 重复定义，假设应为 set_registration_error（注：与setPointError冲突，这里修正）
    setAvatarError = 1205  # 通信数据库设置头像时出现错误
    avatarMissing = 1206  # 头像路径为空

    # 网络相关错误码
    netError = 1300  # 网络错误
    ossError = 1301  # Oss服务器错误
    infoMiss = 1302  # 传输信息缺失
    neo4jError = 1303  # neo4j数据库错误


    # 不存在状态码
    noStatusCode = 0000  # 其他



# @desc: Res返回封装类
class Res:
    def __init__(self,data,statusCode):
        self.data=data
        self.statusCode=statusCode

    @staticmethod
    def Success(data):
        return Res(data,StatusCode.success)

    
    @staticmethod
    def Error(satusCode:int):
        return Res(None,satusCode)    


    def isError(self)->bool:
        return self.statusCode!=StatusCode.success