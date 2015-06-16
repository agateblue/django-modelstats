import datetime
from dateutil.relativedelta import relativedelta

def date_range(start_date, end_date, step='days'):
    kw = {step: 1}
    date_list = []
    while 1:
        new_date = start_date + relativedelta(**kw)
        if new_date < end_date:
            date_list.append(new_date)
        else:
            break
    return date_list
