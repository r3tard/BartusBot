import utils
import static_variables
import reminderStore
import logging

import parsedatetime
from time import mktime
from datetime import datetime, timedelta

plan = utils.Plan()
reminder = reminderStore

class Responses(object):
    def __init__(self):
        self.commands = {
            'SCHEDULE_MON': ('/poniedzialek', '/pon', '/pon@BartusBot'),
            'SCHEDULE_TUE': ('/wtorek', '/wt', '/wt@BartusBot'),
            'SCHEDULE_WED': ('/sroda', '/sr', '/sr@BartusBot'),
            'SCHEDULE_THU': ('/czwartek', '/czw', '/czw@BartusBot'),
            'SCHEDULE_FRI': ('/piatek', '/pt', '/pt@BartusBot'),
            'SCHEDULE_TOMMOROW': ('/jutro', '/j', '/j@BartusBot'),
            'SCHEDULE_NEXT_LESSON': ('/nastepna', '/n', '/n@BartusBot'),
            'SCHEDULE_TODAY': ('/dzisiaj', '/d', '/d@BartusBot'),
            'SCHEDULE_YESTERDAY': ('/wczoraj', 'wczoraj@BartusBot'),
            'HELP': ('/help', '/pomoc', '/pomoc@BartusBot'),
            'MENTION_ALL': ('/wolaj', '/wszyscy', '/wolam', '/wolaj@BartusBot', '/wszyscy@BartusBot'),
            'REMIND': ('/remind',),
            'STATS' : ('/stats', '/stats@BartusBot'),
            'WEEKSTATS': ('/weekstats', '/weekstats@BartusBot'),
        }

    def getReplyForCommand(self, message, chat_id, message_id):
        if message in self.commands['SCHEDULE_MON']:
            return plan.lekcje_dzien(0)
        elif message in self.commands['SCHEDULE_TUE']:
            return plan.lekcje_dzien(1)
        elif message in self.commands['SCHEDULE_WED']:
            return plan.lekcje_dzien(2)
        elif message in self.commands['SCHEDULE_THU']:
            return plan.lekcje_dzien(3)
        elif message in self.commands['SCHEDULE_FRI']:
            return plan.lekcje_dzien(4)
        elif message in self.commands['SCHEDULE_TOMMOROW']:
            return plan.lekcje_dzien(datetime.now().weekday()+1)
        elif message in self.commands['SCHEDULE_NEXT_LESSON']:
            return plan.nastepna_lekcja()
        elif message in self.commands['SCHEDULE_TODAY']:
            return plan.lekcje_dzien(datetime.now().weekday())
        elif message in self.commands['SCHEDULE_YESTERDAY']:
            return plan.lekcje_dzien(datetime.now().weekday()-1)
        elif message in self.commands['HELP']:
            return static_variables.HELP_MESSAGE
        elif message in self.commands['MENTION_ALL']:
            return self.__mentionAll__(chat_id)
        elif message in self.commands['STATS']:
            return self.__stats__(chat_id)
        elif message in self.commands['WEEKSTATS']:
            return self.__week_stats__(chat_id)
        elif self.__isStartingWithCommand__(message, self.commands['REMIND']):
            return self.__remind__(message, chat_id, message_id)


    def __mentionAll__(self, chat_id):
        nicknames = reminderStore.getNicknames(chat_id)
        reply = "Wolam: "
        for nickname in nicknames:
            reply += "@"+str(nickname) + " "
        return reply

    def __remind__(self, message, chat_id, message_id):
            message_id = str(message_id)
            chat_id = str(chat_id)
            date_message_income = datetime.now()
            date_to_remind  = self.__extractTextAndDateFromRemind__(message)["DATE_TO_REMIND"]
            message_to_remind  = self.__extractTextAndDateFromRemind__(message)["MESSAGE_TO_REMIND"]

            reminderStore.putReminderRow(chat_id, date_message_income, date_to_remind, message_to_remind, message_id)
            return "Spoko cumplu przypomne."

    def __stats__(self, chat_id):
        try:
            stats = reminderStore.getStats(str(chat_id))
            msg = self.__renderStats__(stats, "Liczone od: 30 stycznia 2016, 17:00")
        except:
            msg = "Statystyki nie sa dostepne"

        return msg

    def __week_stats__(self, chat_id):
        try:
            stats = reminderStore.getWeekStats(str(chat_id))
            msg = self.__renderStats__(stats, "Liczone od ostatniej niedzieli")
        except:
            msg = "Statystyki nie sa dostepne"

        return msg

    def __isStartingWithCommand__(self, text, commands):
        for command in commands:
            return True if text.startswith(command) else False

    def __extractTextAndDateFromRemind__(self, message):
        message = message[message.find(" ")+1:]
        timestamp = message[:message.find("\"")]
        message_to_remind = message[len(timestamp)+1:len(message)-1]
        if len(message_to_remind) < 1:
            message_to_remind = "Prawilnie przypominam"

        cal = parsedatetime.Calendar()
        cal.parse(timestamp)

        time_struct, parse_status = cal.parse(timestamp)
        date_to_remind = datetime.fromtimestamp(mktime(time_struct))

        return {"MESSAGE_TO_REMIND" : message_to_remind, "DATE_TO_REMIND" : date_to_remind}

    def __renderStats__(self, stats, footer=""):
        msg = "User   :   number of messages  :   %\r\n"
        msg += "----------------------------------"
        count = 0
        for row in stats:
            count += row[1]
        for row in stats:
            percentage = (float(row[1])/float(count))*100.0
            msg += "\r\n" + str(row[0]) + "  :  " + str(row[1]) + "  :  " + str(round(percentage,2)) + "%"

        msg += "\r\n----------------------------------\r\n"
        msg += footer

        return msg