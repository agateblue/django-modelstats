from django.db import models


class Reporter(object):

    def __init__(self, *args, **kwargs):
        pass


    def process(self, queryset, **kwargs):
        report = {}
        report['data'] = self.get_report_content(queryset, **kwargs)
        return report

    def get_report_content(self, queryset, **kwargs):
        return None


class DateTimeReporter(Reporter):

    def __init__(self, *args, **kwargs):
        self.datetime_field = kwargs.pop('datetime_field')
        self.group_by = kwargs.pop('group_by', 'day')

        super(DateTimeReporter, self).__init__(*args, **kwargs)

    def get_report_content(self, queryset, **kwargs):
        return queryset.extra(select={self.group_by: 'date({0})'.format(self.datetime_field)}).values(self.group_by) \
               .annotate(total=models.Count(self.datetime_field))
