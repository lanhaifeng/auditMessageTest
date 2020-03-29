import os


class FileUtil(object):
	"""
	文件工具类
	"""
	@staticmethod
	def get_project_path():
		"""
		获取当前项目路径
		:return:
		"""
		execute_path = os.getcwd()
		return execute_path[:execute_path.find("auditMessageTest\\") + len("auditMessageTest\\")]