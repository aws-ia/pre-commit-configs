from outtrans.base import (
        BaseRaw,
        BaseTransformer,
        convert_annotation
)


class RawData(BaseRaw):

    @property
    def check_name(self):
        return 'CFN Linting'

    @property
    def check_summary(self):
        return 'Errors occured while linting cloudformation templates'


class Transformer(BaseTransformer):

    @property
    def ANNOTATION_MAPPING(self):
        x = {
            'Error': 'failure'
        }
        return x

    @property
    def path(self):
        if self._item['Filename']:
            return self._item['Filename']
        return None

    @property
    def start_line(self):
        return self._item['Start']['LineNumber']

    @property
    def end_line(self):
        return self._item['End']['LineNumber']

    @property
    def start_column(self):
        return self._item['Start']['ColumnNumber']

    @property
    def end_column(self):
        return self._item['End']['ColumnNumber']

    @property
    @convert_annotation
    def annotation_level(self):
        return self._item['Level']

    @property
    def message(self):
        return self._item['Message']

    @property
    def title(self):
        return f"CFN Lint: {self._item['Rule']['ShortDescription']}"

    @property
    def details_url(self):
        return None
