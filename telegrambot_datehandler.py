from datetime import datetime as dt
from datetime import timedelta
from datetime import date
# 1 for single date w/o time, 2 for single date with time, 3 for multiple dates of same timing 4 for discrete


def booking_handler(msg, isMA, booking_type):  # A function that handles both TKPS and MA bookings
    """ Message takes in message.text (Str) as msg
        isMA is the venue. True if its MA
        booking_type specifies how the function is to be run
        All items in booking object is either string or list of strings
        """
    now = dt.now()
    try:
        msg = msg.text
    except AttributeError:
        pass
    msg = msg.replace(' - ', '-')  # Should replace any particular irregularities
    msg = msg.replace('-', ' ')
    msg = msg.split(' ')
    print(msg)
    # Single date handlers
    if len(msg) == 1 and booking_type == 1:
        print("Whole day booking")
        time_in = '0000'
        time_out = '2359'
        book_date = str(msg[0])
        try:
            a = dt.strptime(book_date, "%d%m%y")
            if a.year > now.year + 1 or a.year < now.year:
                return False
        except:
            return False
        booking = Booking(time_in, time_out, book_date,
                          isMA)  # can have if statement here to determine if its audi or tkps
        # call a function in main.py to communicate with g sheets
        print(type(booking))
        return booking
    if len(msg) == 3 and booking_type == 2:  # single booking with time
        print("single day booking with time")
        time_in = str(msg[1])
        time_out = str(msg[2])
        book_date = str(msg[0])
        try:
            dt.strptime(time_in, "%H%M")
            dt.strptime(time_out, "%H%M")
            a = dt.strptime(book_date, "%d%m%y")
            if a.year > now.year + 1 or a.year < now.year:
                return False
        except:
            print("wait why is this returning false???")
            return False
        booking = Booking(time_in, time_out, book_date, isMA)
        print("booking object created")
        return booking
    if len(msg) == 4 and booking_type == 3:  # Multiple bookings with same time
        try:
            d_in = dt.strptime(str(msg[0]), '%d%m%y')
            d_out = dt.strptime(str(msg[1]), '%d%m%y')
            datelist = [d_in.strftime('%d%m%y')]
            if d_in.year > now.year + 1 or d_in.year < now.year:
                return False
        except:
            return False
        day = timedelta(days=1)
        while d_in != d_out:
            d_in = d_in + day
            datelist.append(d_in.strftime('%d%m%y'))
            print(datelist, "datehandler.py")  # Iterates through dates until a list of dates is made
        time_in = str(msg[2])
        time_out = str(msg[3])
        if len(datelist) > 7:
            return False
        try:
            dt.strptime(time_in, "%H%M")
            dt.strptime(time_out, "%H%M")
        except:
            return False
        booking = Booking(time_in, time_out, datelist, isMA)
        return booking  # .book_date is now a List of strings instead of a string


def delete_delay():
    twoweeks = date.today() - timedelta(days=14)
    return dt.combine(twoweeks, dt.min.time())


class Booking:
    def __init__(self, time_in, time_out, book_date, isMA):
        self.time_in = time_in
        self.time_out = time_out
        self.date = book_date
        self.is_ma = isMA
