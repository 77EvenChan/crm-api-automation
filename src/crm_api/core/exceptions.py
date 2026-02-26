class AutomationBaseError(Exception):
	"""框架基础异常类"""
	pass

class APIRequestError(AutomationBaseError):
	"""HTTP请求执行过程中的异常"""
	pass