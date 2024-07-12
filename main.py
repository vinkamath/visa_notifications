import logging
import argparse
import asyncio
import datetime
from typing import Any
from telethon import TelegramClient, errors
from dotenv import load_dotenv

from slots import check_slots_availability
from state import write_state, read_state
from config import AppConfig
from secret import AppSecrets

class App:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.secrets = None
        self.config = None

    def init_app(self) -> None:
        # Load secrets from .env file
        load_dotenv()
        self.secrets = AppSecrets()

        # Parse arguments
        parser = argparse.ArgumentParser(description='Telegram Bot for checking slots availability.')
        parser.add_argument('--test', action='store_true', help='Use test_config.ini instead of config.ini')
        args = parser.parse_args()

        # Initialize configuration
        self.config = AppConfig(args)

        # Configure logging
        logging.basicConfig(level=logging.INFO)

# Newly provided fetch_messages function
    async def fetch_messages(self, client, bot_client, source_group):
        global message_counter
        state = read_state(self.config.state_file_path)
        last_message_id = state.get('last_message_id', 0)
        self.logger.info(f"Read message ID {last_message_id} from f{self.config.state_file_path}")
        message_counter = 0
        heartbeat_interval_seconds = self.config.heartbeat_interval_hours * 3600
        last_heartbeat_time = asyncio.get_event_loop().time()
        self.logger.info(f"Starting to fetch messages from {self.config.source_group_name}...")

        try:
            while True:
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(f"Starting to fetch messages at {current_time}...")

                messages_read = 0  # Initialize message count
                new_last_message_id = last_message_id  # Temporary ID to track the latest message ID in the batch
                messages = []

                async for message in client.iter_messages(source_group, min_id=last_message_id, limit=self.config.message_fetch_limit):
                    if message.id <= last_message_id:
                        self.logger.info(f"Skipping older message #{message.id}. Last message ID {last_message_id}")
                        continue
                    messages_read += 1  # Increment message count
                    new_last_message_id = max(new_last_message_id, message.id)  # Update temporary latest message ID

                    if not message.silent and message.message != '' and check_slots_availability(message.message):
                        messages.append(message)
                    else:
                        self.logger.info(f"❌ #{message.id}: {message.message}")
                        message_counter += 1
            
                count = 0
                while messages:
                    message = messages.pop()
                    try:
                        # Send a message to the target channel
                        if count == self.config.floodwait_delay:
                            count = 0
                            self.logger.info(f"Waiting for {self.config.floodwait_delay} seconds")
                            await asyncio.sleep(self.config.floodwait_delay)
                        await bot_client.send_message(entity=self.config.broadcast_channel_chat_id, message=message.message, silent=False)
                        self.logger.info(f"✅ #{message.id} {message.message}")
                        last_message_id = message.id  # Update the last processed message ID
                        write_state(self.config.state_file_path, {'last_message_id': last_message_id})  # Write state after each message
                    except errors.FloodWaitError as e:
                        self.logger.error(f'Flood wait error when forwarding message. Please wait for {e.seconds} seconds.')
                    except Exception as e:
                        self.logger.error(f'Failed to forward message: {e}')
                    count += 1

                # Update the last processed message ID to the latest one from this batch
                last_message_id = new_last_message_id

                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.logger.info(f"Finished fetching messages at {current_time}. Total messages read: {messages_read}")

                # Check if it's time to send a heartbeat
                current_time = asyncio.get_event_loop().time()
                if current_time - last_heartbeat_time >= heartbeat_interval_seconds:
                    heartbeat_message = f"*I ignored {message_counter} messages in the last {self.config.heartbeat_interval_hours} hours.*"
                    try:
                        await bot_client.send_message(entity=self.config.broadcast_channel_chat_id, message=heartbeat_message, silent=True)
                        self.logger.info(f"Heartbeat message sent: {heartbeat_message}")
                        message_counter = 0  # Reset the counter after sending the heartbeat
                        last_heartbeat_time = current_time
                    except Exception as e:
                        self.logger.error(f"Failed to send heartbeat message: {e}")

                await asyncio.sleep(self.config.message_fetch_interval_seconds)
        except asyncio.CancelledError:
            self.logger.info("Task was cancelled, performing cleanup.")
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received, exiting gracefully.")
        finally:
            await client.disconnect()
            await bot_client.disconnect()
            self.logger.info("Clients disconnected, cleanup done.")

    async def main(self):
        # Initialize clients within the event loop
        self.init_app()
        client = TelegramClient(self.config.client_session_path, self.secrets.api_id, self.secrets.api_hash)
        bot_client = TelegramClient(self.config.bot_session_path, self.secrets.api_id, self.secrets.api_hash)

        await client.start(self.secrets.phone)
        await bot_client.start(bot_token=self.secrets.bot_token)

        try:
            # Get the entity of the source group by its username or ID
            source_group = await client.get_entity(self.config.source_group_name)
            self.logger.debug(f'Connected to source group: {source_group}')
        except errors.FloodWaitError as e:
            self.logger.error(f'Flood wait error. Please wait for {e.seconds} seconds.')
            return
        except errors.UsernameInvalidError:
            self.logger.error('The username is invalid.')
            return
        except errors.UsernameNotOccupiedError:
            self.logger.error('The username is not occupied.')
            return
        except Exception as e:
            self.logger.error(f'An unexpected error occurred: {e}')
            return

        # Start the message fetch and combined heartbeat task
        await self.fetch_messages(client, bot_client, source_group)
if __name__ == "__main__":
    app = App()
    asyncio.run(app.main())
