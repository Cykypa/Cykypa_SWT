# 导入ORM框架:
import json

from sqlalchemy import Column, create_engine, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

with open('./config/config.json') as f:
    data_json = json.loads(f.read())
f.close()
user = data_json['DatabaseConfig']['user']
password = data_json['DatabaseConfig']['password']
Address = data_json['DatabaseConfig']['Address']
DatabaseName = data_json['DatabaseConfig']['DatabaseName']
# 初始化数据库连接:
engine = create_engine(f'mysql+pymysql://{user}:{password}@{Address}/{DatabaseName}')

# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
print("链接数据库成功")


# 定义User对象:
class ClassImage(Base):
    # 表的名字:
    __tablename__ = 'image'

    # 表的结构:
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Project_link = Column(Text, nullable=False, comment="项目链接")
    Image_link = Column(Text, nullable=False, comment="图片链接")
    Image_writing = Column(Text, nullable=False, comment="文本信息")
