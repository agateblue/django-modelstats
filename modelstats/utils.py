import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser

def date_range(start_date, end_date, step='days'):
    try:
        start_date = dateutil.parser.parse(start_date)
        end_date = dateutil.parser.parse(end_date)
    except (AttributeError, ValueError):
        pass

    kw = {step: 1}
    date_list = [start_date]
    previous_date = start_date
    while 1:
        new_date = date_list[-1] + relativedelta(**kw)
        if new_date < end_date:
            date_list.append(new_date)
        else:
            break
    date_list.append(end_date)
    return date_list
