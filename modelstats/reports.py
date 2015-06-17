from django.template.loader import render_to_string
from django.conf import settings

from .utils import ArgsManager


class Report(ArgsManager):
    args_config = {
        'template_name': {
            'required': False,
        },
        'title': {},
        'datasets': {},
    }

    def get_key_verbose_name(self):
        return self.datasets[0].queryset.model._meta.get_field(self.datasets[0].field).verbose_name

    def get_template_name(self):
        default = getattr(settings, 'MODELSTATS_DEFAULT_REPORT_TEMPLATE', 'modelstats/report.html')
        return self.template_name or default

    def render(self):
        return render_to_string(self.get_template_name(), {'report': self})

    def data(self):
        d = []
        for i, row in enumerate(self.datasets[0].data):
            data_row = {}
            key = row['key']
            data_row['key'] = key
            data_row['values'] = []
            for dataset in self.datasets:
                data_row['values'].append(dataset.data[i]['value'])
            d.append(data_row)
        return d
