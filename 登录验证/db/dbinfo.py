# 导入:
from sqlalchemy import Column, String, create_engine, Integer, Text, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()
# 初始化数据库连接:
engine = create_engine('mysql+pymysql://root:111925ly@124.70.106.92:3306/Liu')  # 公司的服务器 MySQL 链接
# engine = create_engine(
#     'sqlite:///./config/sandian.db?check_same_thread=False')  # SQLITE 链接,使用SQLITE必须吧check_same_thread改为false
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


# 定义User对象:
class User(Base):
    # 表的名字:
    __tablename__ = 'admin'
    # 表的结构:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(255), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    role = Column(String(255), nullable=False, comment="角色")
    loginTime = Column(String(255), nullable=False, comment="登录时间")
