# 导入:
from sqlalchemy import Column, create_engine, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

# 初始化数据库连接:
engine = create_engine('mysql+pymysql://root:123456@localhost/image_soider')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


# 定义shangPin对象:
class ImageSpiderIp1(Base):
    # 表的名字:
    __tablename__ = 'image_sprder_ip'
    # 表的结构:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip = Column(Text, nullable=False, comment="ip")
    start_time = Column(Text, nullable=False, comment="插入时间")
    end_time = Column(Text, nullable=False, comment="结束时间")
