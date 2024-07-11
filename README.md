# Visa Notifications
If you're an H1B applicant, you're probably familiar with the pain of constantly checking the USCIS website for visa appointment slots.
There are numerous Telegram groups where users report whether or not visa appointment slots are currently available. However,they are very noisy. Active groups seen over 500 messages a day, 99% of which indicate the inavailability of appointment slots. The groups are noisier when slots become available.

This is a Telegram bot that filters out the noise and will notify you via your own private channel if a slot opens up. Because bots are not allowed to join groups, you can use a user account to fetch messages from the group. **You don't have to admitted to these groups to use this bot.**

## How to use
You can contact me if you would like to use this bot. Or you can choose to host it yourself.

## Setup
### Pre-requisites
1. You will first have to [create a bot](https://telegram.me/BotFather) and get the API token. 
2. Because you will be using a user account to fetch messages from the group, you will also need to get the API ID and API hash from [Telegram](https://core.telegram.org/api/obtaining_api_id).
3. If you want to use a private channel to receive notifications, you will need to get its [channel ID](https://neliosoftware.com/content/help/how-do-i-get-the-channel-id-in-telegram/).

### Running the bot
1. Clone this repository.
2. Install the dependencies using `pip install -r requirements.txt`.
3. Create a `.env` file in the root directory of the project. Add the following variables to the `.env` file:
   ```
    api_id=12345678
	api_hash='12345a3a34a5eb6eecb620amg28g4393'
	phone_number='+11234567890'
	smart_h1b_appt_notification_bot_token='123457893:AAGFebpOBm20bn0GS8T3oeC0K34mKIIoGog'
	private_channel_chat_id=-1002982281657
   ```
4. Run the bot using `python main.py`.
