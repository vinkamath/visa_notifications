import configparser
import os
from typing import Any
from argparse import Namespace


class AppConfig():
	def __init__(self, args: Namespace):
		self.config = configparser.ConfigParser()
		config_file = 'test_config.ini' if args.test else 'config.ini'
		if not os.path.exists(config_file):
			raise FileNotFoundError(f"Config file '{config_file}' not found.")

		self.config.read(config_file)
		self._load_config()

	def _load_config(self) -> None:
		try:
			self.heartbeat_interval_hours = self.config['telegram'].getint('heartbeat_interval_hours', 4)
			self.message_fetch_interval_seconds = self.config['telegram'].getint('message_fetch_interval_seconds', 60)
			self.floodwait_delay = self.config['telegram'].getint('floodwait_delay', 5)
			self.message_fetch_limit = self.config['telegram'].getint('message_fetch_limit', 100)

			self.source_group_name = self.config['telegram']['source_group']
			self.bot_session_path = self.config['telegram'].get('bot_session_name', 'bot_session')
			self.state_file_path = self.config['telegram'].get('state_file_path', 'state_file.txt')
			self.client_session_path = self.config['telegram'].get('client_session_name', 'client_session')
		except KeyError as e:
			raise KeyError(f"Missing required configuration: {e}")