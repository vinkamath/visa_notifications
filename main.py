import os
import logging
import configparser
import argparse
import asyncio
import datetime
from telethon import TelegramClient, errors
from dotenv import load_dotenv

from slots import check_slots_availability

load_dotenv()

# Parse arguments
parser = argparse.ArgumentParser(description='Telegram Bot for checking slots availability.')
parser.add_argument('--test', action='store_true', help='Use test_config.ini instead of config.ini')
args = parser.parse_args()

# Read config
config = configparser.ConfigParser()
config_file = 'test_config.ini' if args.test else 'config.ini'
if os.path.exists(config_file):
    config.read(config_file)
else:
     raise FileNotFoundError(f"Config file '{config_file}' not found.")
bot_name = config['telegram']['bot_name']
heartbeat_interval_hours = int(config['telegram']['heartbeat_interval_hours'])
message_fetch_interval_seconds = int(config['telegram']['message_fetch_interval_seconds'])  # Fetch interval in seconds
source_group_name = config['telegram']['source_group']
bot_session_path = config['telegram']['bot_session_name']
client_session_path = config['telegram']['client_session_name']
floodwait_delay = config['telegram'].getint('floodwait_delay', 5)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('__name_')

# Function to get secret from environment variables or Secret Manager
def get_secret_from_env(secret_id):
    value = os.getenv(secret_id)
    if value is None:
        raise RuntimeError(f"Required environment variable {secret_id} is not set.")
    return value

# Fetch secrets
phone = get_secret_from_env("phone_number")
api_id = get_secret_from_env("api_id")
api_hash = get_secret_from_env("api_hash")
bot_token = get_secret_from_env(bot_name + "_token")
broadcast_channel_chat_id = int(get_secret_from_env("private_channel_chat_id"))

# Newly provided fetch_messages function
async def fetch_messages(client, bot_client, source_group):
    global message_counter
    last_message_id = 0
    message_counter = 0
    heartbeat_interval_seconds = heartbeat_interval_hours * 3600
    last_heartbeat_time = asyncio.get_event_loop().time()
    logger.info(f"Starting to fetch messages from {source_group_name}...")

    try:
        while True:
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Starting to fetch messages at {current_time}...")

            messages_read = 0  # Initialize message count
            new_last_message_id = last_message_id  # Temporary ID to track the latest message ID in the batch
            messages = []

            async for message in client.iter_messages(source_group, min_id=last_message_id, limit=10):
                if message.id <= last_message_id:
                    logger.info(f"Skipping older message #{message.id}. Last message ID {last_message_id}")
                    continue
                messages_read += 1  # Increment message count
                new_last_message_id = max(new_last_message_id, message.id)  # Update temporary latest message ID

                if not message.silent and message.message != '' and check_slots_availability(message.message):
                    messages.append(message)
                else:
                    logger.info(f"❌ #{message.id}: {message.message}")
                    message_counter += 1
        
            count = 0
            while messages:
                message = messages.pop()
                try:
                    # Send a message to the target channel
                    if count == floodwait_delay:
                        count = 0
                        logger.info(f"Waiting for {floodwait_delay} seconds")
                        await asyncio.sleep(floodwait_delay)
                    await bot_client.send_message(entity=broadcast_channel_chat_id, message=message.message, silent=False)
                    logger.info(f"✅ #{message.id} {message.message}")
                except errors.FloodWaitError as e:
                    logger.error(f'Flood wait error when forwarding message. Please wait for {e.seconds} seconds.')
                except Exception as e:
                    logger.error(f'Failed to forward message: {e}')
                count += 1


            # Update the last processed message ID to the latest one from this batch
            last_message_id = new_last_message_id

            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Finished fetching messages at {current_time}. Total messages read: {messages_read}")

            # Check if it's time to send a heartbeat
            current_time = asyncio.get_event_loop().time()
            if current_time - last_heartbeat_time >= heartbeat_interval_seconds:
                heartbeat_message = f"*I ignored {message_counter} messages in the last {heartbeat_interval_hours} hours.*"
                try:
                    await bot_client.send_message(entity=broadcast_channel_chat_id, message=heartbeat_message, silent=True)
                    logger.info(f"Heartbeat message sent: {heartbeat_message}")
                    message_counter = 0  # Reset the counter after sending the heartbeat
                    last_heartbeat_time = current_time
                except Exception as e:
                    logger.error(f"Failed to send heartbeat message: {e}")

            await asyncio.sleep(message_fetch_interval_seconds)
    except asyncio.CancelledError:
        logger.info("Task was cancelled, performing cleanup.")
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, exiting gracefully.")
    finally:
        await client.disconnect()
        await bot_client.disconnect()
        logger.info("Clients disconnected, cleanup done.")

async def main():
    # Initialize clients within the event loop
    client = TelegramClient(client_session_path, api_id, api_hash)
    bot_client = TelegramClient(bot_session_path, api_id, api_hash)

    await client.start(phone)
    await bot_client.start(bot_token=bot_token)

    try:
        # Get the entity of the source group by its username or ID
        source_group = await client.get_entity(source_group_name)
        logger.debug(f'Connected to source group: {source_group}')
    except errors.FloodWaitError as e:
        logger.error(f'Flood wait error. Please wait for {e.seconds} seconds.')
        return
    except errors.UsernameInvalidError:
        logger.error('The username is invalid.')
        return
    except errors.UsernameNotOccupiedError:
        logger.error('The username is not occupied.')
        return
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        return

    # Start the message fetch and combined heartbeat task
    await fetch_messages(client, bot_client, source_group)

if __name__ == "__main__":
    asyncio.run(main())
