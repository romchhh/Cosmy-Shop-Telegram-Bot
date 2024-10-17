# Cosmy Assistant Telegram Bot

Welcome to the **Cosmy Assistant Telegram Bot**! 🚀 This bot is your go-to assistant for managing orders, accessing customer service, and sharing feedback—all within your favorite messaging app, Telegram.

## Features

- **Order History**: Effortlessly retrieve and display your order details, including product information, order status, and total amounts.
- **Support Requests**: Contact customer service directly and get quick responses during our working hours.
- **Ratings & Reviews**: Leave your feedback and ratings on the service received to help us improve!
- **User-Friendly Interface**: Navigate easily through the bot's features with a clean and intuitive design.
- **Asynchronous Operations**: Fast and responsive interactions through async API requests.

## Tech Stack

- **Python** - The backbone of our bot.
- **Aiogram** - For seamless integration with the Telegram Bot API.
- **SQLite** - Lightweight database for managing user data and orders.
- **Cosmy API** - Fetching user and order data efficiently.
- **Pytz** - For managing timezone-related functionalities.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/cosmy-assistant-bot.git
   cd cosmy-assistant-bot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Your Bot**:
   Update the `config.py` file with your Cosmy API keys and Telegram bot token.

4. **Run the Bot**:
   ```bash
   python bot.py
   ```

## Bot Functionality

### Order History

Retrieve your order history effortlessly with just a few taps! The bot uses your phone number and Cosmy API token to fetch your order details.

```python
@dp.callback_query_handler(lambda c: c.data == 'my_order_history')
async def order_history_handler(callback_query: types.CallbackQuery):
    ...
```

### Rating and Review System

Your opinion matters! Rate the service you received and provide feedback directly through the bot. We ensure all feedback reaches our team.

```python
@dp.callback_query_handler(lambda c: c.data.startswith('rate_'), state='*')
async def process_rating(callback_query: types.CallbackQuery, state: FSMContext):
    rating = int(callback_query.data.split('_')[1])
    ...
```

### Contact Center

Need help? Access our contact center with a simple command and connect with the right department for assistance.

```python
@dp.callback_query_handler(lambda c: c.data == 'centre')
async def send_contacts_info(callback_query: types.CallbackQuery):
    ...
```

### Main Menu

Always find your way back! The main menu is just a tap away, letting you navigate through the bot's features with ease.

```python
@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def go_to_main_menu(callback_query: types.CallbackQuery):
    keyboard = get_start_keyboard()
    await callback_query.message.edit_caption(caption="...", reply_markup=keyboard)
```

### Working Hours Enforcement

We value your time! The bot checks whether requests fall within our working hours to provide timely assistance.

```python
def is_within_working_hours():
    kyiv_tz = pytz.timezone('Europe/Kyiv')
    now = datetime.now(kyiv_tz)
    if current_day in WORKING_HOURS:
        ...
    return False
```

## Contributing

We welcome contributions! Here’s how you can help:

1. **Fork the Repository**.
2. **Create a New Branch**: `git checkout -b feature/YourFeature`.
3. **Commit Your Changes**: `git commit -m 'Add some feature'`.
4. **Push Your Branch**: `git push origin feature/YourFeature`.
5. **Open a Pull Request**.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

Feel free to explore, contribute.
