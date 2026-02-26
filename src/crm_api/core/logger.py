import logging
import sys
from pathlib import Path
from crm_api.config.settings import settings

# 动态获取项目根目录并创建 logs 文件夹
ROOT_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

def setup_logger(name: str = "crm-api-automation") -> logging.Logger:
	"""初始化标准日志配置"""
	logger = logging.getLogger(name)
	
	# 简单判断 避免重复绑定 Handler
	if logger.handlers:
		return logger
	
	logger.setLevel(settings.log_level)
	
	# 企业级日志格式
	formatter = logging.Formatter(
		fmt="%(asctime)s | %(levelname)-8s | %(module)s:%(lineno)d | %(message)s",
		datefmt="%Y-%m-%d %H:%M:%S"
	)
	
	# 文件日志
	log_file = LOG_DIR / "automation.log"
	file_handler = logging.FileHandler(log_file, encoding="utf-8")
	file_handler.setFormatter(formatter)
	
	# 控制台日志
	console_handler = logging.StreamHandler(sys.stdout)
	console_handler.setFormatter(formatter)
	
	logger.addHandler(file_handler)
	logger.addHandler(console_handler)
	
	return logger

# 全局暴露日志对象
log = setup_logger()