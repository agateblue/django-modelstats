from persisting_theory import Registry


class DataSetRegistry(Registry):
    look_into = 'reports'

datasets = DataSetRegistry()

class ReportRegistry(Registry):
    look_into = 'reports'

reports = ReportRegistry()
