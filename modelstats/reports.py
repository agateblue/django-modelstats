from django.template.loader import render_to_string

from .utils import ArgsManager


class Report(ArgsManager):
    args_config = {
        'template_name': {
            'default': 'modelstats/report.html',
        },
        'title': {},
        'datasets': {},
    }

    def render(self):
        return render_to_string(self.template_name, {'report': self})

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
