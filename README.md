# @meter_bot

This is my first serious attempt to write a useful Telegram bot in Python.

The idea of this code to demonstrate the possibility of creating a bot for the delivery of electricity, 
water gas, and so on, to make life easier for users who rent apartments.

This bot communicates with the backend (e.g., a rental service) via rest api, collecting 
and retrieving information about tenants' meter readings. 

However, its functionality can be expanded to accept payments, receive information about the apartment, 
collect statistics and manage the rented accommodation.

Hopefully, the bot will make life easier for both tenants and landlords of apartments and offices.

Also, my bot can serve as a template for creating other useful bots.

## Installation
## First
1. [Downlad Python](https://www.python.org/downloads/) (NOT 3.10 VERSION PLEASE)

## Getting started

1. Clone `git@github.com:meinbaumm/meter_bot.git`  
2. Change directory `cd meter_bot`  
3. Install packages `pip3 install -r requirements.txt`
4. [Install Redis](https://redis.io/download) (Using Homebrew `brew install redis`)
5. Start Redis `brew services start redis`
   1. Check Redis is running on your system `redis-cli ping`
   2. If you want to stop Redis `brew services stop redis` or `redis-cli shutdown`
   3. If you want to restore Redis memory:
      1. `redis-cli`
      2. `flushall`
6. `touch config.py && cp config_example.py config.py`
7. Fill in your `config.py` file.
8. Run *(after running backend)* `python3 bot.py`
