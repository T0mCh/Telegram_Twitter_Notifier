###########################################################################
# Twitter Forwarder Bot v0.01 (Console Version)
# By Tom @ 7/6/21
########################################################################### 
# Features: 
# Give a Twitter profile name, and bot will periodically notify you 
# for updated tweets
# 
# Bot Functions to be added (recommended): 
# /start
# /register
# /help
# 
# Before running: 
# please check code @ Line 36 & Line 40
# to provide appropriate Telegram Bot Key, and also target profile name
# 
# Required Modules
# 
# python-telegram-bot 13.5
# install: 
# pip install python-telegram-bot
# 
# pytwitterscraper 1.3.5
# install
# pip install pytwitterscraper
###########################################################################
import logging
import time

from os import write
from typing import Text
from threading import Timer, Thread, Event
from datetime import datetime

from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytwitterscraper import TwitterScraper

class App:
    # To Be Provided: 
    # Format should be: 
    # "##########:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"
    # (10-digit):(35 Characters)
    # Please interact with @botfather to get a new Bot ID for this
    TgToken = "##########:@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

    # To Be Updated: 
    # please change to the twitter profile name you wanted to have Notified
    TwitterProfileName = "elonmusk"


    LastTenTwtrIDs = []
    OldLastTenTwtrIDs = []
    RegisteredChatId = []
    dispatcher = object()
    IsContinue = True
    ProgVal = 0

    tw = TwitterScraper()

    def __init__(self):
        t = Thread(target =self.Twtr_Msg)
        t.start()

    # Enable logging
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )

    logger = logging.getLogger(__name__)

    # Define a few command handlers. These usually take the two arguments update and
    # context.
    def start(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /start is issued."""
        user = update.effective_user
        update.message.reply_markdown_v2(
            fr'Hi {user.mention_markdown_v2()}\!',
            reply_markup=ForceReply(selective=True),
        )
        print("Telegram Bot Status: Start Received")

    def help_command(self, update: Update, _: CallbackContext) -> None:
        """Send a message when the command /help is issued."""
        update.message.reply_text('Help!')

    def echo(self, update: Update, _: CallbackContext) -> None:
        """Echo the user message."""
        update.message.reply_text(update.message.text)
        print("Telegram Bot Status: Echo: " + update.message.text)

    def RegReceive(self, update: Update, _: CallbackContext) -> None:
        chat_id = update.message.chat_id
        self.RegisteredChatId.append(chat_id)
        update.message.reply_text("Registered Chat ID: " + str(chat_id))
        self.SaveChatIds()

    def SaveTwIds(self) -> None:
        f = open("OldTwIds.bin", "w")
        for s in self.OldLastTenTwtrIDs:
            f.write(str(s))
            f.write("\n")
        f.close()

    def ReadTwIds(self) -> None:
        try:
            self.OldLastTenTwtrIDs = []
            f = open("OldTwIds.bin", "r")
            Lines = f.readlines()
            for line in Lines:
                self.OldLastTenTwtrIDs.append(int(line))
            f.close()
        except:
            print("Old Tw File not found")

    def SaveChatIds(self) -> None:
        f = open("TwtrReg.bin", "w")
        for s in self.RegisteredChatId:
            f.write(str(s))
            f.write("\n")
        f.close()

    def ReadChatIds(self) -> None:
        try:
            self.RegisteredChatId = []
            f = open("TwtrReg.bin", "r")
            Lines = f.readlines()
            for line in Lines:
                self.RegisteredChatId.append(int(line))
            f.close()
        except:
            print("Old Reg File not found")

    def TgMain(self) -> None:
        """Start the bot."""
        # Create the Updater and pass it your bot's token.
        updater = Updater(self.TgToken)
        print("Telegram Bot Status: Started")

        # Get the dispatcher to register handlers
        self.dispatcher = updater.dispatcher

        # on different commands - answer in Telegram
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("register", self.RegReceive))

        # on non command i.e message - echo the message on Telegram
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.echo))

        # Start the Bot
        updater.start_polling()

        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        #updater.idle()

    def Twtr_Msg(self) -> None:
        while self.IsContinue:
            try:
                profile = self.tw.get_profile(name=self.TwitterProfileName)
                id = profile.id
                tweets = self.tw.get_tweets(id, count=10)
                for i in tweets.contents:
                    if i['id'] not in self.LastTenTwtrIDs:
                        self.LastTenTwtrIDs.append(i['id'])
                        self.LastTenTwtrIDs.sort(reverse=True)
                        if len(self.LastTenTwtrIDs)>10:
                            self.LastTenTwtrIDs.pop(len(self.LastTenTwtrIDs-1))
                    print(i["text"])

                    if i['id'] not in self.OldLastTenTwtrIDs:
                        print("new Tweet")
                        for j in self.RegisteredChatId:
                            TwtrContent = i['text'] + "\n" + "https://twitter.com/elonmusk/status/" + str(i['id'])
                            self.dispatcher.bot.sendMessage(chat_id=j, text=TwtrContent)

                print(self.LastTenTwtrIDs)
                print("Twitter Latest Post ID: \n" + str(self.LastTenTwtrIDs[0]) +", \n"+str(self.LastTenTwtrIDs[1])+", \n"+str(self.LastTenTwtrIDs[2])+ "\nUpdated @ " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

                self.OldLastTenTwtrIDs = self.LastTenTwtrIDs
                self.SaveTwIds()
                time.sleep(10)
                # self.WaitingNextLoop()
            except:
                self.IsContinue = False

if __name__ == '__main__':
    app = App()
    app.ReadChatIds()
    app.ReadTwIds()
    app.TgMain()