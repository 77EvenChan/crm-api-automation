from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
	"""全局配置管理（Pydantic 模型化）"""
	# 基础环境配置
	base_url: str = "https://api.mock-crm.com/v1"
	timeout: int = 10
	
	# 日志配置
	log_level: str = "INFO"
	
	# 忽略额外的环境变量加载，支持后期平滑接入 .env
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
	
@lru_cache
def get_settings() -> Settings:
	"""单例模式获取配置对象，避免重复实例化"""
	return Settings()

# 全局暴露配置实例
settings = get_settings()