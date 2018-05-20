from telegram.ext import Updater, CommandHandler
import py_expression_eval as pee
import logging
import numpy as np
from matplotlib import pyplot as plt


class EquoBot:
    def __init__(self):
        self.updater = Updater(token='574757973:AAFXdejGo4o'
                                     'UkG-f_vVbyxTF0AA1ZYSoxNk',
                               request_kwargs={'proxy_url':
                                               'https://94.177.216.109:8888'})
        self.dispatcher = self.updater.dispatcher
        self.parser = pee.Parser()

        start_handler = CommandHandler('start', self.start)
        self.dispatcher.add_handler(start_handler)

        help_handler = CommandHandler('help', self.help)
        self.dispatcher.add_handler(help_handler)

        plot_handler = CommandHandler('plot', self.plot)
        self.dispatcher.add_handler(plot_handler)

        list_handler = CommandHandler('list', self.list)
        self.dispatcher.add_handler(list_handler)

    def start(self, bot, update):
        update.message.reply_text('I can draw graphs of certain functions. '
                                  'Type /help for help.')

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
                plt.plot(x, func(x))
            plt.savefig('plot.png')
            plt.clf()
            bot.send_photo(chat_id=update.message.chat_id,
                           photo=open('plot.png', 'rb'))
        except ValueError:
            print('failed')
            update.message.reply_text('Invalid format')

    def help(self, bot, update):
        update.message.reply_text("""
use /plot to draw a graph:
/plot <left border> <right border> <number of points to build on>
<expression> <expression> ... <expression>
Do not use whitespaces inside expressions.

use /list to get the list of available functions
        """)

    def list(self, bot, update):
        update.message.reply_text("""
Arithmetic operators: + - * / % ^
Trigonometric functions: sin(x), cos(x), tan(x)
Inverse ones: asin(x), acos(x), atan(x)
Exponential and natural logarithmic: exp(x), log(x)
Absolute value: abs(x)
Round: round(x), floor(x), ceil(x)
        """)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s -'
                               ' %(levelname)s - %(message)s',
                        level=logging.INFO)
    EquoBot().updater.start_polling()
