import os
import shutil


def get_client_session(client_session_path):

	if os.getenv('ENV') != 'LOCAL':
		modified_client_session_path = "/client_session/" + client_session_path
		client_session_file_path = modified_client_session_path + ".session"
		
		# Check and copy client session file if it exists
		if os.path.exists(client_session_file_path):
			try:
				shutil.copy2(client_session_file_path, client_session_path + ".session")
			except IOError as e:
				raise IOError(f"Failed to copy client session file: {e}")
		else:
			raise FileNotFoundError(f"Client session file not found at {client_session_file_path}")
