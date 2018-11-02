import socket

data_head = 'SA'
separator = '//'
data_tail = 'END'


def get_host_ip():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
	finally:
		s.close()

	return ip


ip_server = get_host_ip()


class StateInfo(object):
	@staticmethod
	def data_format_error():
		return {
			'code': '0000',
			'message': 'data format error'
		}

	@staticmethod
	def data_receive_fail():
		return {
			'code': '0001',
			'message': 'data receive incomplete',
		}

	@staticmethod
	def data_receive_success():
		return {
			'code': '0002',
			'message': 'data receive success',
		}


if __name__ == '__main__':
	print(ip_server)
