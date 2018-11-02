from PyQt5.QtNetwork import QTcpSocket, QTcpServer, QUdpSocket, QHostAddress
from PyQt5 import QtCore


class NetHelper():
	'''TCP/UDP 统一接口类
	## 参数:
	- sock_type='TCP Client'
	- ip='127.0.0.1'
	- port=2007
	'''

	sock = None  # 记录当前连接的sock
	sock_type = None  # 记录当前连接的sock类型

	# ip = None # 记录当前连接的IP地址
	port = None  # 记录当前连接的端口号

	def __init__(self, sock_type='TCP Client', ip='', port=9999):
		'''打开网络设备，建立连接
		## sock_type:
		- 'TCP Client'
		- 'TCP Server'
		- 'UDP'
		'''
		self.sock_type = sock_type
		# self.ip = ip
		self.port = port

		if sock_type == 'TCP Client':
			tcp_client = QTcpSocket()
			tcp_client.connectToHost(ip, port)
			self.sock = tcp_client
		elif sock_type == 'TCP Server':
			tcp_server = QTcpServer()
			tcp_server.listen(QHostAddress(ip), port)
			self.sock = tcp_server
		else:
			print('Unkonw sock_type=%r' % sock_type)

	def close(self):
		'''关闭网络设备，断开连接'''
		if self.sock:
			self.sock.close()
			self.sock = None

	def bytesAvailable(self):
		'''获取可读取数据长度'''
		if self.sock_type == 'TCP Client':
			return self.sock.bytesAvailable()
		elif self.sock_type == 'TCP Server':
			pass
		elif self.sock_type == 'UDP':
			return self.sock.pendingDatagramSize()
		else:
			pass

	def readAll(self):
		'''读取所有数据
		@return:
			tuple(data,[from])
		'''
		if self.sock_type == 'TCP Client':
			data = self.sock.readAll()
			return (data, None)
		elif self.sock_type == 'TCP Server':
			pass
		elif self.sock_type == 'UDP':
			data, host, port = self.sock.readDatagram(self.port)
			data = QtCore.QByteArray(data)
			return (data, [host, port])
		else:
			pass

	def send(self, data, ip_host=None, port_host=None):
		'''发送数据'''
		if self.sock_type == 'TCP Client':
			return self.sock.write(data)
		elif self.sock_type == 'UDP':
			return self.sock.writeDatagram(data, QHostAddress(ip_host), port_host)
		elif self.sock_type == 'TCP Server':
			pass
		else:
			pass

	def readyReadConnect(self, func):
		if self.sock_type == 'TCP Client':
			return self.sock.readyRead.connect(func)
		elif self.sock_type == 'TCP Server':
			pass
		elif self.sock_type == 'UDP':
			return self.sock.readyRead.connect(func)
		else:
			pass
