import requests
import MySQLdb
from threading import Thread
from queue import Queue
from scrapy import Selector
import re
import base64
import os
import threading
from mysql_client_orm import BaiXing
from urllib import parse
import time

# 生产者 and 消费者队列模式

# 存取产品的队列(缓冲区)
My_Queue = Queue()
# 存储url的集合
Url_Set = set()
# 存储res的队列
Res_Queue = Queue()
# 存储data的队列
Data_Queue = Queue()
# 结束信号
signal_ = object

# 放入url的类
class Producer(Thread):
	def __init__(self):
		super().__init__()

	def run(self):
		"""任务函数 -将url放入队列- """
		while True:
			print('producer')
			# 从集合中取出一个url放入队列中
			if len(Url_Set):
				My_Queue.put(Url_Set.pop())
			else:
				print('放入url完成')
				break

# 消费url的类
class Consumer(Thread):
	def __init__(self):
		super().__init__()
	# 下载数据 - 接收参数url
	def download_task(self, url):
		netloc = parse.urlparse(url).netloc
		headers = {
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
			'Accept-Encoding': 'gzip, deflate',
			'Accept-Language': 'zh-CN,zh;q=0.9',
			'Cache-Control': 'max-age=0',
			'Connection': 'keep-alive',
			'Host': netloc,
			'Upgrade-Insecure-Requests': '1',
			'User - Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
							'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
		}
		res = requests.get(url=url, headers=headers)
		time.sleep(2)
		return res
	
	def run(self):
		"""任务函数 -消耗url- """
		while True:
			if not My_Queue.empty():
				print('consumer')
				# 从队列中取出一个url执行下载任务
				url = My_Queue.get()
				# 大致大小
				print('当前需要下载的url还有{}个'.format(My_Queue.qsize()))
				res = self.download_task(url)
				# 返回的响应放入一个队列中
				Res_Queue.put(res)
			else:
				Res_Queue.put(signal_)
				break
# 解析res的类
class Parser(Thread):
	def __init__(self):
		super().__init__()
		self.pattern = re.compile(r'.*?\((.*?)\).*?')
		self.media_path = os.path.join(os.path.dirname(os.getcwd()), 'media')

	# 创建媒体文件夹 - 根据base_url命名 - base_url进行b64加密
	def mkdir_media(self, base_url):
		# 对base_url进行b64加密 - 只是作为文件名来区分
		file_name = base64.b64encode(base_url.encode('utf-8'))
		file_name = str(file_name, 'utf-8')
		file_path = os.path.join(self.media_path,file_name)
		# 在media文件下创建同名文件夹
		if not os.path.exists(file_path):
			os.mkdir(file_path)
		return file_path

	# 根据url判断是图片或者MP4视频文件生成空文件
	def mk_stream_file_name(self, url, file_path):
		pattern = re.compile(r'.*(\..*)$')
		file_type = pattern.match(url).group(1)
		media_file_name = str(base64.b64encode(url.encode('utf-8')), 'utf-8')[:8]
		full_path = os.path.join(file_path, media_file_name, file_type)
		with open(full_path, 'wb') as f:
			return full_path

	# 下载流媒体
	def download_media(self, url, file_path, start, end):
		# 开启下载
		headers = {'Range': 'bytes=%d-%d' % (start, end)}
		r = requests.get(url, headers=headers, stream=True)

		# 写入文件对应位置
		with open(file_path, "rb") as fp:
			fp.seek(start)
			fp.write(r.content)


	# 解析数据 - 接受参数res
	def parse_task(self, res):
		# 获得存储media文件的路径
		url = res.request.url
		# file_path = self.mkdir_media(url)
		selector_res = Selector(res)
		phone_1 = selector_res.xpath('//a[@class="contact-no"]/text()').extract_first()
		phone_2 = selector_res.xpath('//a[@class="show-contact"]/@data-contact').extract_first()
		if phone_1 and phone_2:
			phone = phone_1.replace('*', '') + phone_2
		else:
			phone = ''
		picture_flag = selector_res.xpath('//div[@class="featured-height"]')
		if picture_flag:
			photo_item = picture_flag.xpath('div/a/@style').extract()
			photo_item = ','.join([self.pattern.match(photo_url).group(1) for photo_url in photo_item])
			# 下载保存图片的操作
			picture_url = photo_item
		else:
			picture_url = ''
		video_flag = selector_res.xpath('//source[@type="video/mp4"]')
		if video_flag:
			video_url = video_flag[0].xpath('@src').extract_first(default='')
		else:
			video_url = ''

		data = dict(
			url = url,
			title = selector_res.xpath('//div[@class="viewad-title"]/h1/text()').extract_first(),
			price = selector_res.xpath('//div[@class="viewad-actions"]/span[@class="price"]/text()').extract_first(),
			publish_date = selector_res.xpath('//div[@class="viewad-actions"]/span[2]/text()').extract_first(),
			varieties = selector_res.xpath('//div[@class="top-meta clearfix"]/li[1]/a/text()').extract_first(),
			gender = selector_res.xpath('//div[@class="top-meta clearfix"]/li[2]/span[2]/text()').extract_first(),
			age = selector_res.xpath('//div[@class="top-meta clearfix"]/li[3]/span[2]/text()').extract_first(),
			publisher_id = selector_res.xpath('//span[@class="meta-posterType"]/text()').extract_first(),
			supply_and_demand = selector_res.xpath('//span[@class="meta-供求"]/text()').extract_first(),
			address = selector_res.xpath('//span[@class="meta-address"]/a/text()').extract_first(),
			weChat = selector_res.xpath('//div[@class="weixin-contact-promo"]/'
			                           'div[@class="detail"]/text()').extract_first(default=''),
			ancestry = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[1]/label[2]/text()').extract_first(),
			vaccine = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[3]/label[2]/text()').extract_first(),
			insect = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[4]/label[2]/text()').extract_first(),
			sale_number = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[5]/label[2]/text()').extract_first(),
			trading_place = selector_res.xpath('//div[@class="viewad-detail"]/div[@class="viewad-meta2"]/div[6]/label[2]/text()').extract_first(),
			desc = ','.join(selector_res.xpath('//div[@class="viewad-text-hide"]/text()').extract()),
			picture_url = picture_url,
			video_url = video_url,
		)
		return data

	def run(self):
		"""任务函数 -消耗res- """
		while True:
			if not Res_Queue.empty():
				print('parse')
				# 从队列中取出一个res进行解析
				res = Res_Queue.get()
				if res is signal_:
					Res_Queue.put(signal_)
					break
				print('当前需要解析的res还有{}个'.format(Res_Queue.qsize()))
				data = self.parse_task(res)
				# 放入data队列
				Data_Queue.put(data)



if __name__ == '__main__':
	# 从文本中取出url - 放入set集合中
	with open('id.txt', 'r', encoding='utf-8') as f:
		for line in f.readlines():
			if '请求' in line:
				continue
			else:
				Url_Set.add(line)


	threads = []
	# 放入url
	put_url = Producer()
	threads.append(put_url)
	# 请求url
	for i in range(3):
		get_url = Consumer()
		parse_url = Parser()
		threads.append(get_url)
		threads.append(parse_url)

	for t in threads:
		t.setDaemon(True)
		t.start()
	t.join()
	print('线程执行完成')
	Data_Queue.put(signal_)
	# 入库
	client = BaiXing()
	session = client.conn()
	while True:
		# 创建一条数据
		data = Data_Queue.get()
		if data is signal_:
			break
		new_data = BaiXing(**data)
		# 添加到seesion
		session.add(new_data)
		# 提交
		session.commit()
	session.close()


