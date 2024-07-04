from telethon import TelegramClient, events, errors
import logging
import configparser

from gsecrets import google_secrets
from slots import check_slots_availability

# Read config
config = configparser.ConfigParser()
config.read('config.ini')
googleSecrets_project = config['telegram']['googleSecrets_project']
bot_name = config['telegram']['bot_name']
source_group_name = config['telegram']['source_group']

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Telegram clients
gsm = google_secrets(googleSecrets_project)
api_id = gsm.read_secret("api_id")
api_hash = gsm.read_secret("api_hash")
bot_token = gsm.read_secret(bot_name + "_token")
broadcast_channel_chat_id = int(gsm.read_secret("private_channel_chat_id"))

client = TelegramClient('session_name', api_id, api_hash)
bot_client = TelegramClient('bot_session', api_id, api_hash).start(bot_token=bot_token)

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

    @client.on(events.NewMessage(chats=source_group))
    async def handler(event):
        message = event.message
        if not message.silent and message.message != '' and check_slots_availability(message.message):
            try:
                # Send a message to the target channel
                await bot_client.send_message(entity=broadcast_channel_chat_id, message=message.message, silent=False)
                logger.debug(f"Message {message.message} forwarded to the target group.")
            except errors.FloodWaitError as e:
                logger.error(f'Flood wait error when forwarding message. Please wait for {e.seconds} seconds.')
            except Exception as e:
                logger.error(f'Failed to forward message: {e}')

    print('Listening for new messages...')
    await client.run_until_disconnected()

# Run the client
with client:
    client.loop.run_until_complete(main())
