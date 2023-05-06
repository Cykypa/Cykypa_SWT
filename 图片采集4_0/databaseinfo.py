# 导入ORM框架:
import configparser

from sqlalchemy import Column, create_engine, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 创建对象的基类:
Base = declarative_base()

config = configparser.ConfigParser()
config.read('./config/config.ini', encoding="utf-8")
user = config.get('DatabaseConfig', 'user')
password = config.get('DatabaseConfig', 'password')
Address = config.get('DatabaseConfig', 'Address')
DatabaseName = config.get('DatabaseConfig', 'DatabaseName')

# 初始化数据库连接:
engine = create_engine(f'mysql+pymysql://{user}:{password}@{Address}/{DatabaseName}')

# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
print("链接数据库成功")


# 定义User对象:
class ImageAuthor(Base):
    # 表的名字:
    __tablename__ = 'image_author'
    # 表的结构:
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_name = Column(Text, nullable=False, comment="作者名称")
    author_url = Column(Text, nullable=False, comment="作者主页链接")
    opus_url = Column(Text, nullable=False, comment="作品链接")
    uuid = Column(Text, nullable=False, comment="标识")
