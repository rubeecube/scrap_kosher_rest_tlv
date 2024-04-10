from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
import datetime
import icalendar

TIME_BEFORE_SUNSET = 20
TIME_AFTER_SUNSET = 25
LENGTH_MINHA = 40
LENGTH_ARVIT = 30

location = GeoLocation('Tel Aviv', 32.109333, 34.855499, 'Asia/Jerusalem')
date = datetime.date.today()
calendar = ZmanimCalendar(geo_location=location, date=date)
while date.weekday() != 6:
    date = date - datetime.timedelta(days=1)
date = date - datetime.timedelta(days=7)

calendar = ZmanimCalendar(geo_location=location, date=date)

cal = icalendar.Calendar()
cal.add('prodid', '-//Minha+Arvit//')
cal.add('version', '2.0')

for i in range(52):
    date = date + datetime.timedelta(days=7)
    calendar = ZmanimCalendar(geo_location=location, date=date)
    for ii in range(5):
        date_w = date + datetime.timedelta(days=ii)
        calendar_day = ZmanimCalendar(geo_location=location, date=date_w)
        db = calendar.shkia() - datetime.timedelta(minutes=TIME_BEFORE_SUNSET)
        de = db + datetime.timedelta(minutes=LENGTH_MINHA)

        db = db + datetime.timedelta(days=ii)
        de = de + datetime.timedelta(days=ii)

        event = icalendar.Event()
        event.add('summary', f"Minha (Shkia: {calendar_day.shkia().strftime('%H:%M')})")
        event.add('dtstart', datetime.datetime(db.year, db.month, db.day, db.hour, db.minute // 5 * 5, 0))
        event.add('dtend', datetime.datetime(de.year, de.month, de.day, de.hour, de.minute // 5 * 5, 0))
        event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
        event.add('CLASS', 'PRIVATE')
        cal.add_component(event)

        db_a = db + datetime.timedelta(minutes=TIME_BEFORE_SUNSET + TIME_AFTER_SUNSET + 4)
        de_a = db_a + datetime.timedelta(minutes=LENGTH_ARVIT)

        event = icalendar.Event()
        event.add('summary', f"Arvit (Shkia: {calendar_day.shkia().strftime('%H:%M')})")
        event.add('dtstart', datetime.datetime(db_a.year, db_a.month, db_a.day, db_a.hour, db_a.minute // 5 * 5, 0))
        event.add('dtend', datetime.datetime(de_a.year, de_a.month, de_a.day, de_a.hour, de_a.minute // 5 * 5, 0))
        event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
        event.add('CLASS', 'PRIVATE')
        cal.add_component(event)

f = open('minha_arvit.ics', 'wb')
f.write(cal.to_ical())

