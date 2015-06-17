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
        },
        'year': {
            'required': False,
        },
        'month': {
            'required': False,
        },
        'day': {
            'required': False,
        },
        'sort': {
            'default': 'asc'
        },

    })

    def process_data(self, **kwargs):
        queryset = self.additional_lookups()
        extra = self.get_extra(**kwargs)
        data = queryset.extra(select=extra) \
                       .values(self.group_by) \
                       .annotate(total=models.Count(self.field))
        data = list(data)

        data = sorted(data, key=lambda d: d[self.group_by], reverse = self.sort != 'asc')

        if self.fill_missing_dates:
            data = self._fill_missing_dates(data)
        return data

    def additional_lookups(self):
        """Make additional lookups on queryset, such as specific date filtering"""
        queryset = self.queryset
        if self.year:
            lookup = {'{0}__year'.format(self.field): self.year}
            queryset = queryset.filter(**lookup)

        if self.month:
            lookup = {'{0}__month'.format(self.field): self.month}
            queryset = queryset.filter(**lookup)

        if self.day:
            lookup = {'{0}__day'.format(self.field): self.day}
            queryset = queryset.filter(**lookup)

        return queryset

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
