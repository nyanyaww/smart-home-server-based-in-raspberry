import os, json
from time import time, localtime


class file_operate():
	def __init__(self, path):
		self.root = os.getcwd()
		self.path = path

	def save(self, log_name, log_data):
		self.save_path = "{0}\\{1}".format(self.root, self.path)
		self.json_path = "{0}\\{1}.json".format(self.save_path, log_name)
		if not os.path.exists(self.save_path):
			os.makedirs(self.save_path)
		with open(self.json_path, 'w') as f:
			json.dump(log_data, f)

	def load(self, route):
		with open(route, 'r') as f:
			data = json.load(f)
		return data


def traverse(f):
	fs = os.listdir(f)
	for f1 in fs:
		tmp_path = os.path.join(f, f1)
		if not os.path.isdir(tmp_path):
			print(' ├─%s' % tmp_path)
		else:
			print('%s' % tmp_path)
			traverse(tmp_path)


def local_time(mode=0):
	local_time = localtime(time())
	if mode == 0:
		time_ = '{0}_{1}_{2}_{3}_{4}_{5}'.format(local_time.tm_year, local_time.tm_mon, local_time.tm_mday,
												 local_time.tm_hour, local_time.tm_min, local_time.tm_sec)
	else:
		time_ = time()
	return time_

# save_data = """
# abc
# 123
# 自行车
# *&……%#*-
# 0xff
# """
# f_ = file_operate('192.168.1.1')
# f_.save('日志',save_data)
# print(f_.load(os.getcwd()+'/192.168.1.1/日志.json'))


# rootdir = 'D:/智能家居'
# list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
# print(list)
# for i in range(0, len(list)):
#     path = os.path.join(rootdir, list[i])
#     if os.path.isfile(path):
#         print(os.path.basename(path))

# traverse('D:\\智能家居')
