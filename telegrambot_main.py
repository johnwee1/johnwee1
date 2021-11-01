import telebot
import gspread
from telebot import types
import dateHandler as dh
from datetime import datetime as dt

gc = gspread.service_account('creds.json')
sh = gc.open('newsheet')
sh1 = sh.get_worksheet(0)
sh2 = sh.get_worksheet(1)
sh3 = sh.get_worksheet(2)

API_KEY = "API_KEY" # lol i accidentally committed the api key so i had to delete my entire repo
bot = telebot.TeleBot(API_KEY)
welcome_txt = "Hello! Type anything to start."

def registration(message):
    try:
        if len(message.text.split()) > 1:
            rankname = message.text
            msg = bot.send_message(message.chat.id, "What is your contact number?")
            bot.register_next_step_handler(msg, hp_get, rankname)
        else:
            msg = bot.send_message(message.chat.id, "I think you mistyped. Let's try again...")
            bot.register_next_step_handler(msg, registration)
    except Exception as e:
        print(e)


def hp_get(message, rankname):
    try:
        if len(message.text) == 8:
            hp = int(message.text)
        else:
            raise Exception("oops")
    except Exception:
        msg = bot.send_message(message.chat.id, "Are you sure you sent an 8 digit number? Try again!")
        bot.register_next_step_handler(msg, hp_get, rankname)
    else:
        slot_user(message, rankname, hp)


def slot_user(message, rankname, hp):
    sh3_values = sh3.get_values()
    find_user = sh3.find(str(message.chat.id))
    if find_user is None:
        row_number = len(sh3_values)
        sh1.update('A' + str(row_number + 1), str(rankname))
        sh2.update('A' + str(row_number + 1), str(rankname))
        sh3.update('A' + str(row_number + 1) + ':C' + str(row_number + 1),
                   [[str(rankname), str(message.chat.id), str(hp)]])  # same row but diff column
        bot.send_message(message.chat.id, "New user detected. welcome " + rankname + "!\nYour message ID is "
                         + str(message.chat.id))

    elif find_user.value == str(message.chat.id):
        col = sh3.find(str(message.chat.id)).col
        row = sh3.find(str(message.chat.id)).row
        bot.send_message(message.chat.id, "welcome back, " + sh3.cell(row, col - 1).value + "!")
        bot.send_message(message.chat.id, "You've already signed in. To modify any info/bookings,"
                                          "you need to delete and register your account again. Note: This will delete "
                                          "current bookings")
    else:
        bot.send_message(message.chat.id,
                         "oops, something went wrong. your name is already taken, or you've already signed up!")
        print(find_user.value)


def delete_user(message, f_type):
    """1: deletes user. 2: deletes MA 3:deletes tkps 4:deletes both"""
    try:
        cell_id = sh3.find(str(message.chat.id))  # checks SH 3 for msg id
        col = cell_id.col
        row = cell_id.row
    except:  # An exception is thrown if the assignment fails
        bot.send_message(message.chat.id, "Your user ID hasn't been recorded yet. Can't delete what doesn't exist!")
    else:
        if f_type == 1:
            bot.send_message(message.chat.id, "Your user ID has been deleted, along with all your bookings. You can "
                                          "register your ID again.")
            sh3.update(chr(col - 1 + 64) + str(row) + ':' + chr(col + 1 + 64) + str(row),
                       [['', '', '']])  # clears column and column before
            sh1.update(chr(col - 1 + 64) + str(row), [['']])
            sh2.update(chr(col - 1 + 64) + str(row), [['']])
            # Now to delete the sheet of any empty entries
            sh3_values = sh3.get_values()
            lr3 = sh3_values[-1]
            lr3 = ['' for entry in lr3]
            sh2_values = sh2.get_values()
            lr2 = sh2_values[-1]
            lr2 = ['' for entry in lr2]
            sh1_values = sh1.get_values()
            lr1 = sh1_values[-1]
            lr1 = ['' for entry in lr1]
            sh3_values = [sl for sl in sh3_values if sl[0] != '']
            sh3_values.append(lr3)
            sh2_values = [sl for sl in sh2_values if sl[0] != '']
            sh2_values.append(lr2)
            sh1_values = [sl for sl in sh1_values if sl[0] != '']
            sh1_values.append(lr1)
            sh3.update('A1', sh3_values)
            sh2.update('A1', sh2_values)
            sh1.update('A1', sh1_values)
        else:
            def clear_booking(sht):
                values = sht.get_values()
                values.pop(0) # Removes 1st Row
                c_row = sh3.find(str(message.chat.id)).row
                values = [['' if values[c_row-2].index(y) != 0 else y for y in values[c_row-2]]]
                sht.update('A'+str(c_row), values)

            bot.send_message(message.chat.id, "Your current bookings have been deleted. To change your personal particulars like name or POC contact, type \"delete\" instead")
            if f_type == 2:
                clear_booking(sh1)
            elif f_type == 3:
                clear_booking(sh2)
            elif f_type == 4:
                clear_booking(sh1)
                clear_booking(sh2)
@bot.message_handler(commands=['start', 'Start', 'help'])
def init(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    button1 = types.KeyboardButton('Register')
    button2 = types.KeyboardButton('Delete User')
    button3 = types.KeyboardButton('Book Auditorium')
    button4 = types.KeyboardButton('Book TKPS')
    button5 = types.KeyboardButton("View MA Bookings")
    button6 = types.KeyboardButton("View TKPS Bookings")
    button7 = types.KeyboardButton('Delete MA Bookings')
    button8 = types.KeyboardButton('Delete TKPS Bookings')
    markup.add(button1, button2, button3, button4, button5, button6, button7, button8)
    bot.send_message(message.chat.id, welcome_txt, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def textcmd(message):
    def booking_next_step_handler(isMA, message):
        booking_txt = '''Available Booking Types:
        A) Single date
        B) Single date with timing
        C) Multiple dates with same timings
        D) Multiple dates with multiple timings'''
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        b1 = types.KeyboardButton('A')
        b2 = types.KeyboardButton('B')
        b3 = types.KeyboardButton('C')
        b4 = types.KeyboardButton('D')
        markup.add(b1, b2, b3, b4)
        temp_msg = bot.send_message(message.chat.id, booking_txt, reply_markup=markup)
        bot.register_next_step_handler(temp_msg, booking_selection, isMA=isMA)

    user_id_cell = sh3.find(str(message.chat.id))
    longmsg = message.text.lower()
    msg = message.text.lower().split()  # split into list of strings
    if msg[0] == "register":
        msg = bot.send_message(message.chat.id, "What is your rank and name?")
        bot.register_next_step_handler(msg, registration)
        return
    elif (msg[0] == "delete" or msg[0] == "del") and len(msg) == 1:
        delete_user(message, f_type=1)
    elif (msg[0] == "delete" or msg[0] == "del") and len(msg) > 1:
        if msg[1] == 'tkps':
            delete_user(message, f_type=3)
        elif msg[1] == 'ma' or msg[1] == 'audi':
            delete_user(message, f_type=2)
        elif msg[1] == 'bookings' or msg[1] == 'booking':
            delete_user(message, f_type=4)
        elif msg[1] == 'user':
            delete_user(message, f_type=1)
    elif (longmsg == 'book tkps' or longmsg == 'tkps') and user_id_cell is not None:
        isMA = False
        booking_next_step_handler(isMA, message)
    elif (longmsg == 'book auditorium' or longmsg == 'ma') and user_id_cell is not None:
        isMA = True
        booking_next_step_handler(isMA, message)
    elif longmsg == 'view ma bookings' or longmsg == 'view ma' or msg[0] == 'vma':
        bot.send_message(message.chat.id, printbookings(True))
    elif longmsg == 'view tkps bookings' or longmsg == 'view tkps' or msg[0] == 'vtkps':
        bot.send_message(message.chat.id, printbookings(False))
    else:
        init(message)


def booking_selection(message, isMA):
    """Links from next step handler and calls slot_booking to create booking obj"""
    if message.text == 'A':
        msg = bot.send_message(message.chat.id, "Send the date in which you want to book in the format DDMMYY\n"
                                                "For example, 20th Nov 2021 will be 201121")
        booking_type = 1
        bot.register_next_step_handler(msg, slot_booking, isMA, booking_type)
        return
    elif message.text == 'B':
        msg = bot.send_message(message.chat.id, "Send the date in which you want to book in the following format:\n \n"
                                                "DDMMYY time_in time_out\n \n(Time is in 24 hour format)\n"
                                                "For example: 201121 1000 1800")
        booking_type = 2
        bot.register_next_step_handler(msg, slot_booking, isMA, booking_type)
    elif message.text == 'C':
        msg = bot.send_message(message.chat.id, "Send the dates you want to book in the following format:\n"
                                                "DDMMYY_in DDMMYY_out time_in time_out\n \n"
                                                "The time is in 24 hour format from 0000 to 2359")
        booking_type = 3
        bot.register_next_step_handler(msg, slot_booking, isMA, booking_type)
    elif message.text == 'D':
        msg = bot.send_message(message.chat.id, "Send the dates this format:\n\n"
                                                "<date_1> <time_in> <time_out>\n"
                                                "<date_2> <time_in> <time_out>\n"
                                                "<date_3> <time_in> <time_out>\n"
                                                "<date_4> <time_in> <time_out>\n\n"
                                                "Each new date has to be separated by a new line.\n"
                                                "Dates needs to be given in DDMMYY XXXX YYYY format.\n"
                                                "The bot processes each date as if it were 1 single booking"
                               )
        bot.register_next_step_handler(msg, multiple_dates, isMA) # A special handler for multi-dates

    else:
        bot.send_message(message.chat.id, "Something went wrong... I think I'm slow :(\nType something again?")
        return  # hmm


def slot_booking(message, isMA, booking_type):
    """Creates booking object by calling dateHandler.py, then calls booking_cleaner and handles any failures"""
    booking = dh.booking_handler(message, isMA, booking_type)
    if booking is None:
        bot.send_message(message.chat.id, "Error: Your booking type is none. Please report to maintenance")
        return
    if booking is False:
        bot.send_message(message.chat.id, "Something went wrong - did you type your booking details correctly?")
        return
    if booking.is_ma is True:
        sht = sh1
    else:
        sht = sh2
    value_list = sht.get_values()
    sorted_list = booking_cleaner(value_list, booking)  # Calls booking cleaner function
    if sorted_list is False:
        bot.send_message(message.chat.id, "Your booking has been unsuccessful: ALL date and times specified are in use")
        # PRINT OUT LIST OF BOOKINGS FUNCTION
        return 1 # Return 1 to the booking selector
    elif type(sorted_list) is list:
        sht.update('B2', sorted_list)  # Updates spreadsheet. Uses cleaner syntax now
        user_iterator(booking, message)
        bot.send_message(message.chat.id, "Booking successful! Please double-check your bookings if you are booking multiple dates.")
        return 1 # Return 1 to the booking selector


def user_iterator(booking, message):
    """Function to iterate through the worksheet row to insert new bookings"""

    def booking_iter(booking):
        """Inner function appends new booking date to current list of bookings"""
        for date_index in booking.date:
            row_values.append(date_index)
            row_values.append(booking.time_in)
            row_values.append(booking.time_out)
            print(row_values, " - row values")
        return

    if booking.is_ma is True:
        sht = sh1
    else:
        sht = sh2
    cell_id = sh3.find(str(message.chat.id))
    row_values = sht.row_values(cell_id.row)  # Gets the row of sheet 1,2 and not the misc sheet
    if type(booking.date) is str:
        booking.date = [booking.date]  # Turns str into list with 1 string
    booking_iter(booking)
    sht.update('A' + str(cell_id.row), [row_values])  # Updates the row with the new bookings now


def booking_cleaner(value_list, booking):
    """Cleans all values 2 weeks after they have passed their booking date. Additionally, checks for clashes in
    booking dates, if so, checks the time as well. Returns to slot_booking"""
    two_weeks_ago = dh.delete_delay()
    sort_1 = [[x for x in y if y.index(x) != 0] for y in value_list if value_list.index(y) != 0]
    # Creates a list without the headers (1st col and row)
    print(sort_1, " this is sort 1")
    for elem in sort_1:
        if elem == '':
            continue
        else:
            break  # If element list is non empty, break and run else
    else:
        return sort_1

    # Sort 2 parses date into a Date object while leaving alternate fields intact
    sort_2 = [[dt.strptime(str(x), "%d%m%y") if y.index(x) % 3 == 0 and x != '' else x for x in y] for y in sort_1]
    for x in sort_2: # This for loop deletes dates two weeks ago
        for yz in x:
            if x.index(yz) % 3 == 0 and yz != '':
                if yz < two_weeks_ago:
                    x[x.index(yz) + 2] = ''
                    x[x.index(yz) + 1] = ''
                    x[x.index(yz)] = ''  # Deletes the date and times of the booking
    sort_2 = [[x.strftime("%d%m%y") if y.index(x) % 3 == 0 and x != '' else x for x in y] for y in sort_2]
    for xx in sort_2:
        for yy in xx:
            if xx.index(yy) % 3 == 0 and yy != '':
                """Checks if there is any clashes with the date"""
                if type(booking.date) is list:
                    for item in booking.date:
                        if item == yy:
                            existing_in = int(xx[xx.index(yy) + 1])
                            existing_out = int(xx[xx.index(yy) + 2])
                            intersect = range(max(existing_in, int(booking.time_in) + 1),
                                              min(existing_out, int(booking.time_out) + 1))
                            if len(intersect) != 0:
                                print("""When iterating through sort_2 to check for date, one of the dates clashed.
                            i checked that item against the stated booking time.the timing happened to clash as well
                            hence the booking will not be fulfilled on that particular date""")
                                a = booking.date.pop(booking.date.index(item))
                                print(a)
                                if len(booking.date) == 0:
                                    return False  # Issue - continues booking the other stuff
                elif booking.date == yy:
                    existing_in = int(xx[xx.index(yy) + 1])
                    existing_out = int(xx[xx.index(yy) + 2])
                    intersect = range(max(existing_in, int(booking.time_in) + 1),
                                      min(existing_out, int(booking.time_out) + 1))
                    if len(intersect) != 0:
                        print("The booking timeslot is taken up")
                        return False
    else:
        return sort_2


def multiple_dates(message, isMA):
    """ Parses the multiple dates into something that can iterate through multiple booking objs
    Date time time
    Date time time"""
    msg = message.text
    msg_id = message.chat.id
    datelist = msg.split('\n') # list of dates created
    for item in datelist:
        pseudo_msg = PseudoMsg(item, msg_id)
        slot_booking(pseudo_msg, isMA, 2) # Just iterate through single dates

def printbookings(print_ma):
    """A very rough method of displaying available bookings and respective POCs."""
    if print_ma is True:
        schedule = sh1.get_values()
        string = ast = 'Auditorium Booking Schedule\n\n'
    else:
        schedule = sh2.get_values()
        string = ast = 'Parade Square Booking Schedule\n\n'
    sh3_values = sh3.get_values()
    namelist = [x for row in schedule for x in row if row.index(x) == 0]
    namelist.pop(0)
    datelist = [[x for x in y if y.index(x) != 0] for y in schedule if schedule.index(y) != 0]
    for row in datelist:
        for entry in row:
            try:
                i += 0
            except UnboundLocalError:
                i = 0
            if row.index(entry) % 3 == 0 and entry != '':
                if row.index(entry,i) == 0:
                    string += 'Name: ' + namelist[datelist.index(row)]  + '\n'
                string += entry[0:2] + '/' + entry[2:4] + ': '
                i += 1
            elif row.index(entry,i-1) % 3 == 2 and entry != '':
                string += entry + '\n'
                i += 1
                print(entry, " mod 3 == 2 (should be the last ah) ", row.index(entry))
                if row.index(entry, i-1) == len(row)-1:
                    string += 'Point of Contact: ' + sh3_values[datelist.index(row)+1][2] + '\n'
            elif row.index(entry,i-1) % 3 == 1 and entry != '':
                print(entry, " mod 3 == 1 ", row.index(entry))
                string += entry + ' to '
                i += 1
    if string == ast:
        string += "There are currently no bookings for the venue."
    return string

class PseudoMsg:
    def __init__(self, text, chat_id):
        self.text = text
        self.chat = PseudoChat(chat_id)

class PseudoChat:
    def __init__(self, id):
        self.id = id
print("program start")
bot.infinity_polling()
