from outtrans.base import (
        BaseRaw,
        BaseTransformer,
        convert_annotation
)


class RawData(BaseRaw):

    @property
    def check_name(self):
        return 'TFN Linting'

    @property
    def check_summary(self):
        return 'Errors occured while linting terraform files'

    @property
    def iterate_key(self):
        return 'issues'


class Transformer(BaseTransformer):

    @property
    def ANNOTATION_MAPPING(self):
        x = {
            'warning': 'failure'
        }
        return x

    @property
    def path(self):
        if self._item['range']['filename']:
            return self._item['range']['filename']
        return None

    @property
    def start_line(self):
        return self._item['range']['start']['line']

    @property
    def end_line(self):
        return self._item['range']['end']['line']

    @property
    def start_column(self):
        return None

    @property
    def end_column(self):
        return None

    @property
    @convert_annotation
    def annotation_level(self):
        return self._item['rule']['severity']

    @property
    def message(self):
        return self._item['message']

    @property
    def title(self):
        return f"tflint: {self._item['rule']['name']}"

    @property
    def details_url(self):
        return self._item['rule']['link']
