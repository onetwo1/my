import requests
import MySQLdb
from threading import Thread
from queue import Queue


# 生产者 and 消费者队列

# 存取产品的队列(缓冲区)
My_Queue = Queue()
# 存储url的集合
Url_Set = set()
# 存储res的队列
Res_Queue = Queue()
# 存储data的队列
Data_Queue = Queue()

# 放入url的类
class Producer(Thread):
	def __init__(self, name):
		# 线程的名字
		self.name = name
		Thread.__init__(self, name)
	
	def run(self):
		"""任务函数 -将url放入队列- """
		while True:
			# 如果队列没有满
			if My_Queue.not_full():
				# 从集合中取出一个url放入队列中
				My_Queue.put(Url_Set.pop())

# 消费url的类
class Consumer(Thread):
	def __init__(self, name):
		self.name = name
		Thread.__init__(self, name)
	
	# 下载数据 - 接收参数url
	def download_task(url):
		res = requests.get(url=url)
		return res
	
	def run(self):
		"""任务函数 -消耗url- """
		while True:
			# 如果队列不为空
			if My_Queue.not_empty():
				# 从队列中取出一个url执行下载任务
				url = My_Queue.get()
				res = self.download_task(url)
				# 返回的响应放入一个队列中
				Res_Queue.put(res)
				
# 解析res的类
class Parser(Thread):
	def __init__(self, name):
		self.name = name
		Thread.__init__(self, name)
	
	# 解析数据 - 接受参数res
	def parse_task(res):
		pass
	
	def run(self):
		"""任务函数 -消耗res- """
		while True:
			if Res_Queue.not_empty():
				# 从队列中取出一个res进行解析
				res = Res_Queue.get()
				'''
				title                - 标题
				price                - 价格
				publish_date         - 发布时间
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
				data = self.parse_task(res)
				# 放入data队列
				Data_Queue.put(data)

# 存储data的类
# 直接使用twisted的异步框架



# 保存数据 - 接收参数data
def save_task(data):
	# 链接数据库
	conn = MySQLdb.connect('localhost', 'root', '1139409573', 'baixing', charset='utf-8', use_unicode=False)
	# 获取cursor
	cursor = conn.cursor()
	# 创建插入语句
	insert_sql = ''
	# 执行插入语句
	cursor.execute(insert_sql, ())
	# 提交
	cursor.commit()


if __name__ == '__main__':
	
	# 从文本中取出url - 放入set集合中
	with open('id.txt', 'r', encoding='utf-8') as f:
		for line in f.readlines():
			if '请求' in line:
				continue
			else:
				Url_Set.add(line)
	


	