from telethon import TelegramClient, events, errors
import logging

from my_secrets import googleSecrets
from slots import check_slots_availability

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

gsm = googleSecrets("smart-visa-notifications")
# Create the client and connect
client = TelegramClient('session_name', gsm.read_secret("api_id"), gsm.read_secret("api_hash"))
# Use a bot to trigger app notifications
bot_client = TelegramClient('bot_session', gsm.read_secret("api_id"), gsm.read_secret("api_hash"))
bot_client.start(bot_token = gsm.read_secret("smart_h1b_appt_notification_bot_token"))

broadcast_channel_chat_id = gsm.read_secret("private_channel_chat_id")

async def main():
    try:
        # Get the entity of the source group by its username or ID
        source_group = await client.get_entity('@H1B_H4_Visa_Dropbox_slots')
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

    async for message in client.iter_messages(source_group, limit=200):
        if not message.silent and message.message != ''and check_slots_availability(message.message):
            try:
                # Send a message to the target channel 
                await bot_client.send_message(entity=int(broadcast_channel_chat_id), message=message.message, silent=False)
                logger.debug(f"Message {message.message} forwarded to the target group.")
            except errors.FloodWaitError as e:
                logger.error(f'Flood wait error when forwarding message. Please wait for {e.seconds} seconds.')
            except Exception as e:
                logger.error(f'Failed to forward message: {e}')

# Run the client
with client:
    client.loop.run_until_complete(main())
