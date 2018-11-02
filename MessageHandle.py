import config
from datetime import datetime
import os, json

__test_command = '0020'
__test_message = 'the message is used for test'


class MessageHandle(object):
	data_from_device = b''
	send_data = ''
	data_format = 'ascii'

	def __init__(self):
		pass

	@staticmethod
	def __bytes2str(bytes_: bytes):
		try:
			return str(bytes_, encoding='utf-8')
		except Exception:
			return str(bytes_, encoding='gbk')

	@staticmethod
	def __str2bytes(string_: str):
		return bytes(string_, encoding='utf8')

	@property
	def parsing(self):
		"""
		文本的解析,把bytes转化为str 并且返回解析后的结果
		"""
		data_list = self.__bytes2str(self.data_from_device).split(config.separator)
		# print(data_list)
		'''
		0 - 数据头
		1 - ip号
		2 - 长度校验
		3 - 时间戳
		4 - 命令
		5 - 文本信息
		6 - 数据尾
		'''
		if data_list[0] == 'SA' and data_list[6] == 'END':
			if int(data_list[2]) == len(data_list[4] + data_list[5]):
				return data_list[1], data_list[4], data_list[5]
			else:
				return '数据接收不完整'
		else:
			return '数据接收格式错误'

	@parsing.setter
	def parsing(self, data_from_device):
		"""
		赋值
		"""
		self.data_from_device = data_from_device

	@property
	def encoding(self):
		"""
		文本的编码,把文本编码成16进制或者ascii,返回值是bytes
		"""
		send_message_list = []
		if self.data_format == '16' or self.data_format == 16:
			for each in self.send_data:
				temp = hex(ord(each))
				send_message_list.append(self.__str2bytes(temp))
		elif self.data_format == 'ascii':
			for each in self.send_data:
				send_message_list.append(self.__str2bytes(each))
		msg = b''.join(send_message_list)
		return msg

	@encoding.setter
	def encoding(self, encoding_info: tuple):
		self.send_data, self.data_format = encoding_info

	def save(self, path, data):
		"""
		:param path: 存储的文件夹名
		:param data: 存储数据
		:return: None
		"""
		root = os.getcwd()
		path = root + '/' + path
		now_time_list = self.local_time().split('_')
		now_time = '{0}_{1}_{2}'.format(now_time_list[0], now_time_list[1], now_time_list[2])
		if not os.path.exists(path):
			os.makedirs(path)
		file_name = path + '/' + "{}.json".format(now_time)
		# 保存数据之前如果旧数据存在则读取旧数据
		if os.path.exists(file_name):
			with open(file_name, 'r') as f:
				old_data = json.load(f)
				data = str(old_data) + str(data) + '\n'
		with open(file_name, 'w') as f:
			json.dump(data, f, indent=4)

	@staticmethod
	def load(path, file_name):
		root = os.getcwd()
		path = root + '/' + path
		file_name = path + '/' + "{}.json".format(file_name)
		with open(file_name, 'r') as f:
			return json.load(f)

	def info_connect(self, ip_address, command, message):
		byte_num = str(len(command) + len(message))
		info = "{1}{0}{2}{0}{3}{0}{4}{0}{5}{0}{6}{0}{7}".format(
			config.separator, config.data_head,
			ip_address, byte_num, self.local_time(),
			command, message, config.data_tail)
		return info

	@staticmethod
	def local_time():
		now = datetime.now()
		return now.strftime('%Y_%m_%d_%H_%M_%S')


if __name__ == '__main__':
	test_message = MessageHandle()
	message_from_device = test_message.info_connect(config.ip_server, __test_command, __test_message)
	# print(message_from_device)

	test_message.parsing = message_from_device.encode('utf-8')
# test_message.save('test', """
# 'asd':'aasd',
# 'asda':'asdasd'
# """)
# print(test_message.load('192.168.1.171', '2018_10_31'))
# print(test_message.parsing)
