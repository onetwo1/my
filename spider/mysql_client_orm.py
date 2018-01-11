from sqlalchemy import String, Column, create_engine, Integer, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# 创建基类
Base = declarative_base()


# 数据表类
class BaiXing(Base):
    def __init__(self):
        __tablename__ = 'BaiXing'
        # 表结构
        '''
        id                   - 主键
        url                  - 请求的url
        title                - 标题
        price                - 价格
        publish_date         - 发布时间
        h_publish_date       - 历史发布时间
        varieties            - 品种
        gender               - 性别
        age                  - 年龄
        publisher_id         - 发布人身份
        supply_and_demand    - 供求
        address              - 地址
        phone                - 手机号
        weChat               - 微信号
        ancestry             - 血统
        vaccine              - 疫苗情况
        insect               - 驱虫情况
        sale_number          - 待售只数
        trading_place        - 交易地点
        desc                 - 描述
        picture_url          - 照片链接 是一个列表 存放多个照片的url
        video_url            - 视频链接 应该只要一个即可
        '''
        id = Column(Integer, primary_key=True, autoincrement=True)
        url = Column(String(200))
        title = Column(String(200))
        price = Column(String(200))
        publish_date = Column(String(200))
        h_publish_date = Column(String(200))
        varieties = Column(String(200))
        gender = Column(String(200))
        age = Column(String(200))
        publisher_id = Column(String(200))
        supply_and_demand = Column(String(200))
        address = Column(String(200))
        phone = Column(String(200))
        weChat = Column(String(200))
        ancestry = Column(String(200))
        vaccine = Column(String(200))
        insect = Column(String(200))
        sale_number = Column(String(200))
        trading_place = Column(String(200))
        desc = Column(Text)
        picture_url = Column(String(200))
        video_url = Column(String(200))

        # 初始化数据库链接
        engine = create_engine('mysql+mysqldb://root:1139409573@localhost:3306/baixing?charset=utf8',
                               convert_unicode=True)
        # 创建数据表
        Base.metadata.create_all(engine)

        # 创建数据库链接
        self.db_session = sessionmaker(bind=engine)

    def conn(self):
        # 创建一个链接实例
        session = self.db_session()
        return session
