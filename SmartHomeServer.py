# coding: utf-8
# qt类
from PyQt5.QtWidgets import QMessageBox, QComboBox, QFileDialog, QLabel, QPushButton, QSizePolicy, QSpacerItem, \
	QStatusBar, QDialog
from PyQt5.QtGui import QIcon
from PyQt5 import uic
# python的类
from datetime import datetime
import binascii
import os
# 用户写的类4
from NetHelper import NetHelper
from MessageHandle import MessageHandle
from config import ip_server, StateInfo

material = 'material'  # 存储图片素材的目录

ui_file = os.getcwd() + "/{}/smart_home_server.ui".format(material)
ui_main_window, qt_base_class = uic.loadUiType(ui_file)

version = '1.05'


class SmartHomeServer(ui_main_window, qt_base_class):
	connected = False  # 连接状态
	proto = None  # 记录当前协议类型
	address_local = None  # 本地主机地址
	address_remote = None  # 远程主机地址
	hex_view = False  # 十六进制显示标志
	time_view = False  # 显示接收时间标志
	net = None  # 当前网络连接 NetHelper类
	hex_send = None  # 十六进制发送标志
	save_file = None  # 接收转向文件标志
	save_file_name = None  # 接收转向文件名（全路径）

	client_list = []  # 记录所有连接的TCP 客户端
	client_list_device = {}  # 记录真实的设备列表
	message = MessageHandle()  # 消息的编码 解码 读取 储存
	state = StateInfo()  # 返回信息的状态

	# status_bar上添加的控件

	# 使用字典方式进行管理
	status_bar_dict = {}
	rx_count = 0
	tx_count = 0

	# status_bar End

	def __init__(self):
		# 窗体与基础qt类的初始化
		ui_main_window.__init__(self)
		qt_base_class.__init__(self)
		self.setupUi(self)
		self.comboBox_protocol.addItems(['TCP Server', 'TCP Client'])
		self.comboBox_local.addItems([ip_server, '127.0.0.1'])
		self.comboBox_port.addItems(['8086'])
		self.setWindowIcon(QIcon('./{}/meow.ico'.format(material)))
		self.setWindowTitle(u'服务器-智能家居...by 老喵喵 ver{0}'.format(version))
		# 给状态栏添加控件
		self.init_status_bar()

	def init_status_bar(self):
		# 设置status_bar所有控件自动延伸
		self.statusbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		# 设置status隐藏控制点（靠齐最右边）
		self.statusbar.setSizeGripEnabled(False)

		self.status_bar_dict['status'] = QLabel()
		self.status_bar_dict['status'].setText('状态：Ready')
		self.status_bar_dict['tx'] = QLabel()
		# self.status_bar_dict['space']=QSpacerItem(20,20,QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.status_bar_dict['tx'].setText('发送计数：0')
		self.status_bar_dict['rx'] = QLabel()
		self.status_bar_dict['rx'].setText('接收计数：0')
		self.status_bar_dict['clear'] = QPushButton()
		self.status_bar_dict['clear'].setText('清除')
		self.status_bar_dict['clear'].setToolTip('清除发送和接收计数')

		self.status_bar_dict['clear'].pressed.connect(
			self.status_bar_clear_pressed)

		for i, w in enumerate(self.status_bar_dict.values()):
			if i != len(self.status_bar_dict) - 1:
				self.statusbar.addWidget(w, 20)
			else:
				# 最后一个控件不拉伸
				self.statusbar.addWidget(w)

	def status_bar_clear_pressed(self):
		self.status_bar_dict['tx'].setText('发送计数：0')
		self.status_bar_dict['rx'].setText('接收计数：0')
		self.rx_count = 0
		self.tx_count = 0

	def __view(self, data, prefix=''):
		"""显示数据
		# data:
			需要显示的原始数据（binary）
		# prefix:
			需要显示的前缀（string）
		"""

		self.rx_count += len(data)
		self.status_bar_dict['rx'].setText('接收计数：%s' % self.rx_count)

		if self.hex_view:
			# 转换成十六进制数
			data = data.toHex()
		if self.save_file and self.save_file_name:
			# 接收转向文件
			# with open(self.save_file_name, 'wb') as f:
			#     f.write(data)
			pass
		data = bytearray(data)  # 转成python的bytes类型，方便处理
		try:
			s = data.decode('gbk')
			if self.time_view:
				# 显示接收时间
				now = datetime.now()
				s = '[%s] ' % now.strftime('%Y-%m-%d %H:%M:%S,%f') + s

			if self.hex_view:
				s = s.upper()
			self.textBrowser.append(prefix + s)

		except Exception:
			QMessageBox.critical(self, '错误', '数据编码有误！可尝试十六进制显示。')

	def data_receive(self):
		"""
		数据接收（TCP Client/UDP）
		:return: None
		"""
		if self.net:
			while self.net.bytesAvailable() > 0:
				data, host = self.net.readAll()  # Qbytearray类型
				# 字符出错 Qbytearray转化失败
				if host:
					ip = host[0].toString()
					port = host[1]
					host = '[From %s:%s] ' % (ip, port)
				else:
					host = ''
				self.__view(data, prefix=host)

	def slot_proto_change(self, proto):
		"""
		协议类型更改
		"""
		if proto == 'TCP Server':
			self.label_host.setText(u'客户端：')
			self.comboBox_host.addItem(u'所有连接')
			self.pushButton_host.setText(u'断开连接')
		else:
			self.label_host.setText(u'远程主机：')
			self.comboBox_host.clear()
			self.pushButton_host.setText(u'清除主机')

	def slot_connect(self):
		"""
		打开（连接）按钮按下
		"""

		# 下一个状态，与当期状态取反（用于显示提示信息）
		next_state = not self.connected

		if next_state:
			if self.net_connect():
				self.connected = next_state
				next_state = not self.connected

				self.status_bar_dict['status'].setText('状态：打开')
		else:
			if self.net_disconnect():
				self.connected = next_state
				next_state = not self.connected
				self.status_bar_dict['status'].setText('状态：关闭')

		dict_next = {True: '打开', False: '关闭'}
		self.pushButton_connect.setText(dict_next[next_state])

		self.comboBox_protocol.setEnabled(next_state)
		self.comboBox_local.setEnabled(next_state)
		self.comboBox_port.setEnabled(next_state)

	def net_connect(self):
		"""
		连接打开
		"""
		self.proto = self.comboBox_protocol.currentText()
		ip = self.comboBox_local.currentText()
		port = self.comboBox_port.currentText()

		try:
			port = int(port)
			if self.proto == 'TCP Client':
				self.net = NetHelper(sock_type='TCP Client', ip=ip, port=port)
			elif self.proto == 'TCP Server':
				self.net = NetHelper(sock_type='TCP Server', ip=ip, port=port)
				# 绑定客户端连接消息
				self.net.sock.newConnection.connect(self.tcp_server_on_connection)
			else:
				pass
		except:  # Exception as e:
			# self.sock = None
			QMessageBox.critical(self, '错误', self.tr('地址:%s，端口:%s ，连接失败！' % (ip, port)), QMessageBox.Ok, QMessageBox.Ok)

		if self.net:
			# 绑定接收
			self.net.readyReadConnect(self.data_receive)

		return self.net is not None

	def net_disconnect(self):
		"""
		连接关闭
		"""
		if self.net:
			try:
				if self.proto == 'TCP Server':
					# 断开所有客户端，并清除client_list
					client_list_temp = self.client_list.copy()
					try:
						for client_temp in client_list_temp:
							# 调用会触发 disconnect，其中包含删除self.client_list中数据
							client_temp.close()
					except:
						pass
					self.client_list.clear()

				self.net.close()
				self.net = None
			except Exception as e:
				print(e)
		return self.net is None

	def __send(self, b):
		"""发送数据
		@b:
			binary数据
		"""
		ret = 0  # 记录成功发送的字节数

		if self.proto == 'TCP Server':
			host = self.comboBox_host.currentText()
			match_client = True  # 只发送给一个客户端
			if host == u'所有连接':
				match_client = False
			else:
				ip_host, port_host = host.split(':')
				port_host = int(port_host)
			for client in self.client_list:
				if match_client is True:
					if client.peerAddress().toString() == ip_host and client.peerPort() == port_host:
						# 找到对应的client
						send_test = bytes(self.message.info_connect(ip_server, '9999', str(b, encoding='utf-8')),
										  encoding='utf8')
						ret = client.write(send_test)
				elif match_client is False:
					send_test = bytes(self.message.info_connect(ip_server, '9999', str(b, encoding='utf-8')),
									  encoding='utf8')
					ret = client.write(send_test)
		elif self.proto == 'TCP Client':
			# 测试
			send_test = bytes(self.message.info_connect('device1', '9999', str(b, encoding='utf-8')), encoding='utf8')
			ret = self.net.send(send_test)

		self.tx_count += ret
		self.status_bar_dict['tx'].setText('发送计数：%s' % self.tx_count)

	def slot_send(self):
		"""
		发送按钮按下事件
		"""
		if self.net:
			text = self.textEdit_send.toPlainText()
			if text:
				try:
					if self.hex_send:
						text = text.replace(' ', '')  # 删除无效的空格
						if len(text) % 2 != 0:
							# 十六进制发送输入的长度必须是2的倍数
							raise Exception('十六进制输入的长度必须是2的倍数')
						b = binascii.a2b_hex(text)
					else:
						b = bytes(text, encoding='utf-8')
					self.__send(b)

				except binascii.Error as e:
					QMessageBox.critical(self, '错误', '十六进制数中包含非法字符！', QMessageBox.Ok, QMessageBox.Ok)
				except Exception as e:
					QMessageBox.critical(self, '错误', '%s' % e, QMessageBox.Ok, QMessageBox.Ok)
			else:
				QMessageBox.critical(self, '错误', '数据为空！', QMessageBox.Ok, QMessageBox.Ok)
		else:
			QMessageBox.critical(self, '错误', '请先打开连接！', QMessageBox.Ok, QMessageBox.Ok)

	def slot_hex_view_change(self, state):
		"""
		十六进制显示更改
		"""
		self.hex_view = True if state else False

	def slot_time_view_change(self, state):
		"""
		显示接收时间更改
		"""
		self.time_view = True if state else False

	def slot_clear_view(self):
		"""
		清除显示
		"""
		if self.textBrowser.toPlainText():
			self.textBrowser.clear()

	def slot_save_view(self):
		"""
		保存显示
		"""
		if not self.textBrowser.toPlainText():
			# 没有数据直接退出
			return

		file_name, state = QFileDialog.getSaveFileName(self, '保存文件', './', 'Text文件(*.txt)')
		if state:
			with open(file_name, 'w') as f:
				f.write(self.textBrowser.toPlainText())
			QMessageBox.information(self, '成功', '%s文件保存成功! ' % file_name)

	def tcp_server_on_connection(self):
		"""
		TCP Server有客户端连接进来
		"""
		client = self.net.sock.nextPendingConnection()
		client.readyRead.connect(self.tcpServer_dataRecvie)
		# 客户端退出绑定clientExit
		client.disconnected.connect(self.tcpServer_clientExit)
		# client.error.connect(self.tcpServer_clientExit)

		self.client_list.append(client)

		ip = client.peerAddress().toString()
		port = client.peerPort()
		client_info = '%s:%s' % (ip, port)
		self.comboBox_host.addItem(client_info)

		self.statusbar.showMessage('客户端：%s 成功连接！' % client_info, msecs=5000)

	def tcpServer_clientExit(self):
		"""
		TCP Server下客户端退出（正常断开/异常退出）
		"""
		client = self.sender()
		try:
			client.close()
			self.client_list.remove(client)
		except:
			pass

		ip = client.peerAddress().toString()
		port = client.peerPort()
		client_info = '%s:%s' % (ip, port)
		self._comboBox_removeItem_byName(self.comboBox_host, client_info)
		self.statusbar.showMessage('客户端：%s 断开连接！' % client_info, msecs=5000)

	def _comboBox_removeItem_byName(self, combo, name):
		'''QComboBox中删除特定名字的项目'''
		for i in range(0, combo.count()):
			if name == combo.itemText(i):
				# 找到对应的项目
				combo.removeItem(i)

	def tcpServer_dataRecvie(self):
		'''TCP Server数据处理'''
		if self.net:
			for client in self.client_list:
				if client.bytesAvailable() > 0:
					ip = client.peerAddress().toString()
					port = client.peerPort()
					client_info = '[From %s:%s] ' % (ip, port)

					data = client.readAll()  # data为QByteArray对象
					b_data = data.data()  # b_date为bytes对象

					print('原生数据：{}'.format(b_data))

					self.message.parsing = b_data  # 解析bytes变为字符串
					self.message.save(ip, self.message.parsing)
					self.__message_handle(ip, port)

					# test start
					# print(ip, port)

					# test end

					self.__view(data, prefix=client_info)

	def __message_handle(self, ip, port):
		"""
		根据解析的数据来处理
		"""

		if self.message.parsing == '数据接收格式错误':
			send_source = self.state.data_format_error()
		elif self.message.parsing == '数据接收不完整':
			send_source = self.state.data_receive_fail()
		else:
			send_source = self.state.data_receive_success()
		send_message = self.message.info_connect(ip_server, send_source['code'], send_source['message'])

		# 数据编码二进制 以ascii形式发出
		self.message.encoding = (send_message, 'ascii')

		# 找到对应的设备 发送返回的数据
		for client in self.client_list:
			if client.peerAddress().toString() == ip and client.peerPort() == port:
				client.write(self.message.encoding)
		print('解析数据：{0}'.format(self.message.parsing))
		print('发送给客户端的数据：{0}'.format(self.message.encoding))
		print()

	def slot_hex_send_change(self, state):
		"""
		十六进制发送
		"""
		self.hex_send = True if state else False

	def slot_host_clear(self):
		"""
		清除主机/断开客户端
		"""

		if self.client_list:
			# 断开客户端
			clients = self.client_list.copy()
			host = self.comboBox_host.currentText()
			ip, port = host.split(':')
			for c in clients:
				if c.peerAddress().toString() == ip and int(port) == c.peerPort:
					c.close()
		else:
			self.comboBox_host.clearEditText()
			self.comboBox_host.clear()

	def slot_input_clear(self):
		'''清除输入'''
		if self.textEdit_send.toPlainText():
			self.textEdit_send.clear()

	def slot_input_from_file(self):
		'''文件发送'''

		# self.file_send=True

		file_name, state = QFileDialog.getOpenFileName(self, u'打开文件', './', u'所有文件(*.*)')
		if state:
			with open(file_name, 'rb') as f:
				b = f.read()
				self.__send(b)

	def slot_save_view_file_change(self, state):
		'''接收转向文件'''
		self.save_file = True if state else False
		if state:
			file_name, ok = QFileDialog.getSaveFileName(self, u'保存文件', './', u'所有文件(*.*)')
			if ok:
				self.save_file_name = file_name
		else:
			self.save_file_name = None
