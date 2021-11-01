### telegram-bot
## The python bot uses pyTelegramBotAPI as a front-end GUI replacement to book venues (and counter-check if there was any bookings made prior).

The code is not designed to accommodate a variable amount of booking venues, and has to be manually modified to accommodate more than 2.
The database is a private Google Sheet somewhere safe, and the bot uses the gspread API to leverage sheets as a makeshift database

Due to the limitations of Google Cloud, which restricts excessive API calling to a crazy amount, this essentially rules out iteration through the sheet itself (like in Excel).
The price of an API call for both the entire sheet value and a single cell is the same.
I can only do 100 requests per 100 seconds per user, which forces me to work with nested lists and what-have-you a lot more than I'd like.

However that said, this project serves to be a great beginners' exercise in using APIs, both with gspread and pyTelegramBotAPI, and a great exercise in list comprehension, nested loops, datetime parsing, my first dabble in OOP (with the Booking class) and pretty much programming something that operates outside a console in general. Mostly though, its list comprehension because Sheets is basically a 2D list. Back in that particular point in time, I had yet to use NumPy arrays - though I am learning as I'm going along.

In the meantime I also learnt how to use basic github to code from camp and at home and sync whenever.

SPEAKING OF SYNC - this bot (at the moment) is not programmed asynchronously, and I frankly don't plan to do that for this project, seeing as concurrent users are almost always zero.
