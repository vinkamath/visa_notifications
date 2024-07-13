import os

class AppSecrets():
	def __init__(self,):
		self.read_secrets()

	def get_secret_from_env(self, secret_id):
		value = os.getenv(secret_id)
		if value is None:
			raise RuntimeError(f"Required environment variable {secret_id} is not set in .env")
		return value

	def read_secrets(self,):
		self.phone = self.get_secret_from_env("phone_number")
		self.api_id = self.get_secret_from_env("api_id")
		self.api_hash = self.get_secret_from_env("api_hash")
		self.bot_name = self.get_secret_from_env("bot_name")
		self.bot_token = self.get_secret_from_env("bot_token")
		self.broadcast_channel_chat_id = int(self.get_secret_from_env("private_channel_chat_id"))
