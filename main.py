import os
import logging
import configparser
import threading
from telethon import TelegramClient, events, errors
from dotenv import load_dotenv

from slots import check_slots_availability

load_dotenv()

# Read config
config = configparser.ConfigParser()
config.read('config.ini')
bot_name = config['telegram']['bot_name']
source_group_name = config['telegram']['source_group']
bot_session_path = config['telegram']['bot_session_name']
client_session_path = config['telegram']['client_session_name']

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

# Use the original paths for creating the clients
client = TelegramClient(client_session_path, api_id, api_hash).start(phone)
bot_client = TelegramClient(bot_session_path, api_id, api_hash).start(bot_token=bot_token)

async def main():

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

    #async for message in client.iter_messages(source_group, limit=200):
    @client.on(events.NewMessage(chats=source_group))
    async def handler(event):
        message = event.message
        if message.message:
            logger.info(f"Processing message: {message.message}")
        if not message.silent and message.message != '' and check_slots_availability(message.message):
            try:
                # Send a message to the target channel
                await bot_client.send_message(entity=broadcast_channel_chat_id, message=message.message, silent=False)
                logger.info(f"✅Message {message.message} forwarded to the target group.")
            except errors.FloodWaitError as e:
                logger.error(f'Flood wait error when forwarding message. Please wait for {e.seconds} seconds.')
            except Exception as e:
                logger.error(f'Failed to forward message: {e}')
        else:
            logger.info(f"❌Discarding message: {message.message}")
            
    print('Listening for new messages...')
    await client.run_until_disconnected()

# Run the client
with client:
    client.loop.run_until_complete(main())
