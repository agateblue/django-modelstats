import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser


class ArgsManager(object):
    def __init__(self, **kwargs):
        for kw_name, kw_value in kwargs.items():
            try:
                config = self.args_config[kw_name]
            except KeyError:
                raise ValueError(' {0} is not a valid argument for this function'.format(kw_name))

        for arg_name, arg_config in self.args_config.items():
            v = kwargs.get(arg_name, arg_config.get('default'))
            if v is None and arg_config.get('required', True):
                raise ValueError('Missing {0} argument'.format(arg_name))
            setattr(self, arg_name, v)


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
