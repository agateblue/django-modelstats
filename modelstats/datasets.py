from django.db import models
from django.db import connection


class DataSet(object):
    """Gather data from a given queryset"""

    config = [
        ('queryset', None),
        ('title', ''),
    ]

    def __init__(self, *args, **kwargs):
        for config_key, default_value in self.config:
            v = kwargs.get(config_key, default_value)
            if v is None:
                raise ValueError('Missing {0} argument'.format(config_key))
            setattr(self, config_key, v)

    def get_config(self, **kwargs):
        config = {}
        for config_key, default_value in self.config:
            config[config_key] = kwargs.get(config_key, getattr(self, config_key))
        return config

    def process(self):
        self.data = self.process_data()
        return self

    def process_data(self, queryset, **kwargs):
        return []



class DateTimeDataSet(DataSet):
    config = DataSet.config + [
        ('datetime_field', None),
        ('group_by', 'day'),
    ]

    def process_data(self, **kwargs):
        extra = self.get_extra(**kwargs)
        return self.queryset.extra(select=extra) \
                       .values(self.group_by) \
                       .annotate(total=models.Count(self.datetime_field))

    def get_extra(self, **kwargs):
        if self.group_by == 'day':
            return {self.group_by: 'date({0})'.format(self.datetime_field)}
        if self.group_by in ['month', 'year']:
            truncate_date = connection.ops.date_trunc_sql(self.group_by, self.datetime_field)
            return {self.group_by: truncate_date}
