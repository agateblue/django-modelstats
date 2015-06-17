import datetime
from dateutil.relativedelta import relativedelta

from django.db import models
from django.db import connection

from . import utils


class DataSet(utils.ArgsManager):
    """Gather data from a given queryset"""

    args_config = {
        'queryset': {},
        'title': {
            'required': False,
        }
    }



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
            'default': True,
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
        'start_date': {
            'required': False,
        },
        'end_date': {
            'required': False,
            'default': None,
            'cast': lambda v: datetime.date.today() if v == 'today'  else v
        }

    })
    @property
    def date_format(self):
        if self.group_by == 'day':
            return '%Y/%m/%d'
        if self.group_by == 'month':
            return '%Y/%m'
        if self.group_by == 'year':
            return '%Y'

    def process_data(self, **kwargs):
        queryset = self.additional_lookups()
        extra = self.get_extra(**kwargs)
        data = queryset.extra(select=extra) \
                       .values('key') \
                       .annotate(value=models.Count(self.field))
        data = list(data)
        if len(data) == 0:
            return data
        data = self.clean_keys(data)
        data = sorted(data, key=lambda d: d['key'], reverse = self.sort != 'asc')

        if self.fill_missing_dates:
            data = self._fill_missing_dates(data)
        return data

    def clean_keys(self, data):
        new_data = []

        for row in data:
            raw_key = row['key']
            try:
                key = row['key'].strftime(self.date_format)
            except AttributeError:
                key = row['key']
            new_row = {
                'key': key,
                'value': row['value'],
                'raw_key': raw_key,
            }
            new_data.append(new_row)
        return new_data

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

        if self.start_date:
            lookup = {
                '{0}__gte'.format(self.field): self.start_date
            }
            queryset = queryset.filter(**lookup)

        if self.end_date:
            lookup = {
                '{0}__lte'.format(self.field): self.end_date
            }
            queryset = queryset.filter(**lookup)

        return queryset

    def _fill_missing_dates(self, data):
        """When grouping by date, having no record for a date means the date is not present
        in results. This method correct this"""
        start_date, end_date = self.start_date or data[0]['raw_key'], self.end_date or data[-1]['raw_key']
        if start_date == end_date:
            return data
        print(start_date, end_date)
        all_dates = utils.date_range(start_date, end_date, step='{0}s'.format(self.group_by))
        data_dates = [row['key'] for row in data]
        missing = sorted(set([d.strftime(self.date_format) for d in all_dates]) - set(data_dates))
        print(all_dates, missing)
        new_data = []
        offset = 0
        data_length = len(data)
        print(data)

        for i, date in enumerate(all_dates):
            formated_date = date.strftime(self.date_format)
            new_row = {}
            if formated_date in missing:
                offset += 1
                new_data.append({'key': formated_date, 'value': 0})
                new_row['key'] = formated_date
                new_row['raw_key'] = date
                new_row['value'] = 0
            else:
                new_row = data[i - offset]
                new_row['key'] = formated_date
            new_data.append(new_row)
        return new_data

    def get_extra(self, **kwargs):
        if self.group_by == 'day':
            return {'key': 'date({0})'.format(self.field)}
        if self.group_by in ['month', 'year']:
            truncate_date = connection.ops.date_trunc_sql(self.group_by, self.field)
            return {'key': truncate_date}
