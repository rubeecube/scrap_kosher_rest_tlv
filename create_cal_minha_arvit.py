from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
from zmanim.hebrew_calendar.jewish_calendar import JewishCalendar
import datetime
import icalendar
import argparse

TIME_BEFORE_SUNSET = 20
TIME_AFTER_SUNSET = 25
LENGTH_MINHA = 40
LENGTH_ARVIT = 30


def get_day_type(jewish_date):
    """
    Determine if a date is a holiday, Chol HaMoed, Rosh Chodesh, or regular day.
    Returns tuple: (event_type, event_name)
    event_type can be: 'ooo_holiday', 'chol_hamoed', 'rosh_hodesh', 'free_event', 'regular'
    """
    sig_day = jewish_date.significant_day()
    
    # OOO holidays - major holidays where work is prohibited
    OOO_HOLIDAYS = {
        'rosh_hashana': 'Rosh Hashanah',
        'yom_kippur': 'Yom Kippur',
        'shemini_atzeres': 'Shemini Atzeret',
        'simchas_torah': 'Simchat Torah',
        'tisha_beav': 'Tisha B\'Av',
        'purim': 'Purim',
    }
    
    # Free events - holidays observed but work is permitted
    FREE_EVENTS = {
        'erev_rosh_hashana': 'Erev Rosh Hashanah',
        'tzom_gedalyah': 'Tzom Gedalyah',
        'erev_yom_kippur': 'Erev Yom Kippur',
        'erev_succos': 'Erev Sukkot',
        'hoshana_rabbah': 'Hoshana Rabbah',
        'chanukah': 'Chanukah',
        'tenth_of_teves': 'Asara B\'Tevet',
        'tu_beshvat': 'Tu B\'Shvat',
        'taanis_esther': 'Ta\'anit Esther',
        'shushan_purim': 'Shushan Purim',
        'purim_katan': 'Purim Katan',
        'shushan_purim_katan': 'Shushan Purim Katan',
        'erev_pesach': 'Erev Pesach',
        'pesach_sheni': 'Pesach Sheni',
        'lag_baomer': 'Lag BaOmer',
        'erev_shavuos': 'Erev Shavuot',
        'seventeen_of_tammuz': 'Shiva Asar B\'Tammuz',
        'tu_beav': 'Tu B\'Av',
        'yom_hashoah': 'Yom HaShoah',
        'yom_hazikaron': 'Yom HaZikaron',
        'yom_haatzmaut': 'Yom Ha\'atzmaut',
        'yom_yerushalayim': 'Yom Yerushalayim',
    }
    
    # Check for Chol HaMoed first (takes priority)
    if sig_day == 'chol_hamoed_succos':
        return ('chol_hamoed', 'Chol HaMoed Sukkot')
    elif sig_day == 'chol_hamoed_pesach':
        return ('chol_hamoed', 'Chol HaMoed Pesach')
    
    # Check for Sukkot and Pesach - need special handling for Israeli observance
    if sig_day == 'succos':
        # First day of Sukkot (15 Tishrei) is OOO in Israel
        if jewish_date.jewish_day == 15:
            return ('ooo_holiday', 'Sukkot (1st Day)')
        else:
            # 2nd day in diaspora would be here, but we treat as Chol HaMoed in Israel
            return ('chol_hamoed', 'Chol HaMoed Sukkot')
    
    if sig_day == 'pesach':
        # 15 Nissan (1st day) and 21 Nissan (7th day) are OOO in Israel
        if jewish_date.jewish_day == 15:
            return ('ooo_holiday', 'Pesach (1st Day)')
        elif jewish_date.jewish_day == 21:
            return ('ooo_holiday', 'Pesach (7th Day)')
        else:
            # Middle days are Chol HaMoed
            return ('chol_hamoed', 'Chol HaMoed Pesach')
    
    if sig_day == 'shavuos':
        return ('ooo_holiday', 'Shavuot')
    
    # Check OOO holidays
    if sig_day in OOO_HOLIDAYS:
        return ('ooo_holiday', OOO_HOLIDAYS[sig_day])
    
    # Check free events
    if sig_day in FREE_EVENTS:
        event_name = FREE_EVENTS[sig_day]
        # Special handling for Chanukah
        if sig_day == 'chanukah':
            day_num = jewish_date.day_of_chanukah()
            if day_num:
                event_name = f'Chanukah (Day {day_num})'
        return ('free_event', event_name)
    
    # Check for Rosh Chodesh
    if jewish_date.is_rosh_chodesh():
        month_name = jewish_date.jewish_month_name()
        return ('rosh_hodesh', f'Rosh Chodesh {month_name}')
    
    return ('regular', None)


def get_start_date_for_jewish_year(jewish_year):
    """Get the Sunday before or on 1 Tishrei of the given Jewish year."""
    jc = JewishCalendar()
    jc.set_jewish_date(jewish_year, 7, 1)  # 1 Tishrei = Rosh Hashanah
    start_date = datetime.date(jc.gregorian_year, jc.gregorian_month, jc.gregorian_day)
    
    # Find the Sunday before or on this date
    while start_date.weekday() != 6:  # 6 = Sunday
        start_date = start_date - datetime.timedelta(days=1)
    
    return start_date


def main():
    parser = argparse.ArgumentParser(
        description='Generate Minha/Arvit calendar with Jewish holidays',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate for Jewish year 5786
  python create_cal_minha_arvit.py --jewish-year 5786
  
  # Generate for current date + 52 weeks
  python create_cal_minha_arvit.py --weeks 52
  
  # Generate from specific date
  python create_cal_minha_arvit.py --start-date 2025-09-21 --weeks 52
        '''
    )
    
    parser.add_argument('--jewish-year', type=int, 
                        help='Jewish year (e.g., 5786). Generates full year from Rosh Hashanah.')
    parser.add_argument('--start-date', type=str,
                        help='Start date in YYYY-MM-DD format (default: last Sunday)')
    parser.add_argument('--weeks', type=int, default=52,
                        help='Number of weeks to generate (default: 52)')
    parser.add_argument('--output', type=str, default='minha_arvit.ics',
                        help='Output filename (default: minha_arvit.ics)')
    
    args = parser.parse_args()
    
    # Determine start date
    if args.jewish_year:
        date = get_start_date_for_jewish_year(args.jewish_year)
        num_weeks = 52
        print(f"Generating calendar for Jewish year {args.jewish_year}")
        print(f"Starting from: {date}")
    elif args.start_date:
        date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
        num_weeks = args.weeks
        print(f"Generating calendar from {date} for {num_weeks} weeks")
    else:
        # Default: use current Jewish year
        jc = JewishCalendar()
        jc.set_gregorian_date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        current_jewish_year = jc.jewish_year
        date = get_start_date_for_jewish_year(current_jewish_year)
        num_weeks = args.weeks
        print(f"Generating calendar for current Jewish year {current_jewish_year}")
        print(f"Starting from: {date}")
    
    location = GeoLocation('Tel Aviv', 32.109333, 34.855499, 'Asia/Jerusalem')
    calendar = ZmanimCalendar(geo_location=location, date=date)

    cal = icalendar.Calendar()
    cal.add('prodid', '-//Minha+Arvit//')
    cal.add('version', '2.0')

    for i in range(num_weeks):
        date = date + datetime.timedelta(days=7)
        calendar = ZmanimCalendar(geo_location=location, date=date)
        
        # Check all 7 days of the week for holidays and special days
        for ii in range(7):
            date_w = date + datetime.timedelta(days=ii)
            calendar_day = ZmanimCalendar(geo_location=location, date=date_w)
            
            # Create JewishCalendar object for this date
            jewish_cal = JewishCalendar()
            jewish_cal.set_gregorian_date(date_w.year, date_w.month, date_w.day)
            
            # Check what type of day this is
            day_type, day_name = get_day_type(jewish_cal)
            
            # Add holiday events
            if day_type == 'ooo_holiday':
                # All-day out-of-office event for major holidays
                event = icalendar.Event()
                event.add('summary', f'[JCal] {day_name} - Out of Office')
                event.add('dtstart', datetime.date(date_w.year, date_w.month, date_w.day))
                event.add('dtend', datetime.date(date_w.year, date_w.month, date_w.day) + datetime.timedelta(days=1))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
                continue  # Skip Minha/Arvit for OOO holidays
            
            elif day_type == 'chol_hamoed':
                # All-day event for Chol HaMoed
                event = icalendar.Event()
                event.add('summary', f'[JCal] {day_name} - Out of Office')
                event.add('dtstart', datetime.date(date_w.year, date_w.month, date_w.day))
                event.add('dtend', datetime.date(date_w.year, date_w.month, date_w.day) + datetime.timedelta(days=1))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
                continue  # Skip Minha/Arvit for Chol HaMoed
            
            elif day_type == 'rosh_hodesh':
                # Morning OOO until 10:30 AM for Rosh Hodesh
                event = icalendar.Event()
                event.add('summary', f'[JCal] {day_name} - Out of Office (Morning)')
                event.add('dtstart', datetime.datetime(date_w.year, date_w.month, date_w.day, 0, 0, 0))
                event.add('dtend', datetime.datetime(date_w.year, date_w.month, date_w.day, 10, 30, 0))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
                # Continue to add Minha/Arvit for Rosh Hodesh
            
            elif day_type == 'free_event':
                # All-day FREE event for other Jewish calendar days
                event = icalendar.Event()
                event.add('summary', f'[JCal] {day_name}')
                event.add('dtstart', datetime.date(date_w.year, date_w.month, date_w.day))
                event.add('dtend', datetime.date(date_w.year, date_w.month, date_w.day) + datetime.timedelta(days=1))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'FREE')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
                
                # Special handling for Chanukah: Add OOO from Minha to Tset Hakochavim + 1hr
                if 'Chanukah' in day_name:
                    # Calculate Minha time
                    minha_start = calendar_day.shkia() - datetime.timedelta(minutes=TIME_BEFORE_SUNSET)
                    # Calculate Tset Hakochavim (nightfall) + 1 hour using proper zmanim method
                    tset_hakochavim = calendar_day.tzais()
                    tset_plus_1hr = tset_hakochavim + datetime.timedelta(hours=1)
                    
                    event = icalendar.Event()
                    event.add('summary', f'[JCal] {day_name} - Candle Lighting')
                    event.add('dtstart', datetime.datetime(minha_start.year, minha_start.month, minha_start.day, 
                                                          minha_start.hour, minha_start.minute // 5 * 5, 0))
                    event.add('dtend', datetime.datetime(tset_plus_1hr.year, tset_plus_1hr.month, tset_plus_1hr.day,
                                                        tset_plus_1hr.hour, tset_plus_1hr.minute // 5 * 5, 0))
                    event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                    event.add('CLASS', 'PRIVATE')
                    cal.add_component(event)
                # Continue to add Minha/Arvit for free events
            
            # Add winter time OOO blocks (November through February)
            # Winter months: 11, 12, 1, 2
            if date_w.weekday() < 5 and date_w.month in [11, 12, 1, 2]:
                # First winter OOO block: 13:10 - 13:45
                event = icalendar.Event()
                event.add('summary', 'Winter Break 1')
                event.add('dtstart', datetime.datetime(date_w.year, date_w.month, date_w.day, 13, 10, 0))
                event.add('dtend', datetime.datetime(date_w.year, date_w.month, date_w.day, 13, 45, 0))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
                
                # Second winter OOO block: 15:10 - 15:30
                event = icalendar.Event()
                event.add('summary', 'Winter Break 2')
                event.add('dtstart', datetime.datetime(date_w.year, date_w.month, date_w.day, 15, 10, 0))
                event.add('dtend', datetime.datetime(date_w.year, date_w.month, date_w.day, 15, 30, 0))
                event.add('X-MICROSOFT-CDO-BUSYSTATUS', 'OOF')
                event.add('CLASS', 'PRIVATE')
                cal.add_component(event)
            
            # Add Minha and Arvit only for weekdays (Sunday-Thursday, 0-4 in Python)
            if date_w.weekday() < 5:
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

    # Write calendar to file
    with open(args.output, 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"\n✓ Calendar generated successfully!")
    print(f"✓ Output file: {args.output}")


if __name__ == '__main__':
    main()

