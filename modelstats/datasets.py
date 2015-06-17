from django.db import models
from django.db import connection

from . import utils

class Required(object):
    pass

class DataSet(object):
    """Gather data from a given queryset"""

    args_config = {
        'queryset': {},
        'title': {
            'required': False,
        }
    }


    def __init__(self, *args, **kwargs):
        for arg_name, arg_config in self.args_config.items():
            v = kwargs.get(arg_name, arg_config.get('default'))
            if v is None and arg_config.get('required', True):
                raise ValueError('Missing {0} argument'.format(arg_name))
            setattr(self, arg_name, v)

    def process(self):
        self.data = self.process_data()
        return self

    def process_data(self, queryset, **kwargs):
        return []



class DateDataSet(DataSet):
    args_config = dict(DataSet.args_config, **{
        'field': {},
        'group_by': {
            'default': 'day',
        },
        'fill_missing_dates': {
            'default': False,
        }

    })

    def process_data(self, **kwargs):
        extra = self.get_extra(**kwargs)
        data = self.queryset.extra(select=extra) \
                       .values(self.group_by) \
                       .annotate(total=models.Count(self.field))
        data = list(data)
        if self.fill_missing_dates:
            data = self._fill_missing_dates(data)
        return data

    def _fill_missing_dates(self, data):
        """When grouping by date, having no record for a date means the date is not present
        in results. This method correct this"""
        start_date, end_date = data[0][self.group_by], data[-1][self.group_by]
        dates = utils.date_range(start_date, end_date, step='{0}s'.format(self.group_by))
        new_data = []
        offset = 0
        for i, date in enumerate(dates):
            formated_date = date.strftime("%Y-%m-%d")
            try:
                if data[i-offset][self.group_by] == formated_date:
                    new_data.append({self.group_by: formated_date, 'total': data[i-offset]['total']})
                else:
                    offset += 1
                    new_data.append({self.group_by: formated_date, 'total': 0})
            except IndexError:
                break
        return new_data

    def get_extra(self, **kwargs):
        if self.group_by == 'day':
            return {self.group_by: 'date({0})'.format(self.field)}
        if self.group_by in ['month', 'year']:
            truncate_date = connection.ops.date_trunc_sql(self.group_by, self.field)
            return {self.group_by: truncate_date}
