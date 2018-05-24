from telegram.ext import Updater, CommandHandler
import py_expression_eval as pee
import logging
import numpy as np
from matplotlib import pyplot as plt
import os


class EquoBot:
    def __init__(self):
        """Creating command handlers"""
        self.updater = Updater(token="574757973:AAFXdejGo4o"
                                     "UkG-f_vVbyxTF0AA1ZYSoxNk",
                               request_kwargs={"proxy_url":
                                               "https://94.177.216.109:8888"})
        self.dispatcher = self.updater.dispatcher
        self.parser = pee.Parser()

        start_handler = CommandHandler("start", self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler("help", self.help)
        self.dispatcher.add_handler(help_handler)

        list_handler = CommandHandler("list", self.list)
        self.dispatcher.add_handler(list_handler)

        plot_handler = CommandHandler("plot", self.plot)
        self.dispatcher.add_handler(plot_handler)

        last_handler = CommandHandler("last", self.last)
        self.dispatcher.add_handler(last_handler)

        clear_handler = CommandHandler("clear", self.clear)
        self.dispatcher.add_handler(clear_handler)

    def get_text(self, filename):
        """Retrieve text from a file"""
        f = open(filename, "r")
        s = ""
        for line in f:
            s += line
        return s

    def invalid_format(self, bot, id):
        """In case the user entered something wrong ¯\_(ツ)_/¯"""
        print("failed")
        bot.send_message(chat_id=id, text="Invalid format")

    def start(self, bot, update):
        update.message.reply_text(self.get_text("start.txt"))

    def help(self, bot, update):
        update.message.reply_text(self.get_text("help.txt"))

    def list(self, bot, update):
        """List functions, combinations of which can be plotted"""
        update.message.reply_text(self.get_text("list.txt"))

    def save_query(self, id, query):
        id = str(id)
        if id not in os.listdir("history"):
            os.chdir("history")
            os.system("touch {}".format(id))
            os.chdir("..")
        with open("history/{}".format(id), "a") as file:
            file.write(query + '\n')

    def clear(self, bot, update):
        """Clear query history for a particular user"""
        id = str(update.message.chat_id)
        if id in os.listdir("history"):
            os.remove("history/{}".format(id))
            bot.send_message(chat_id=id, text="History cleared")
        else:
            bot.send_message(chat_id=id, text="No items to clear")

    def plot(self, bot, update):
        try:
            args = update.message.text.split()
            # left and right borders of the segment on which to draw
            left, right = map(float, args[1:3])
            # number of points
            precision = int(args[3])
            for expression in args[4:]:
                def func(x):
                    return self.parser.parse(expression).evaluate({'x': x})
                # allowing it to accept a vector
                func = np.vectorize(func)
                x = np.linspace(left, right, precision)
                plt.plot(x, func(x), label=expression)
                self.save_query(update.message.chat_id, expression)
            plt.legend(loc="best")
            plt.savefig("plot.png")
            bot.send_photo(chat_id=update.message.chat_id,
                           photo=open("plot.png", "rb"))
            plt.clf()
            os.remove("plot.png")
        except Exception:
            plt.clf()
            self.invalid_format(bot, update.message.chat_id)

    def last(self, bot, update):
        """Retrieve last n queries done by a particular user"""
        id = str(update.message.chat_id)
        try:
            reply = ""
            n = int(update.message.text.split()[1])
            if id not in os.listdir("history"):
                update.message.reply_text("No recent queries.")
            else:
                queries = open("history/{}".format(id), "r").readlines()
                size = len(queries)
                if size < n:
                    reply = "only {} saved queries exist:\n".format(size)
                    n = size
                for i in range(n):
                    reply += queries[len(queries) - n + i]
                update.message.reply_text(reply)
        except Exception:
            self.invalid_format(bot, update.message.chat_id)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s -'
                               ' %(levelname)s - %(message)s',
                        level=logging.INFO)
    EquoBot().updater.start_polling()
