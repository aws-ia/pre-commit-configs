from dataclasses import dataclass
from dataclasses_jsonschema import JsonSchemaMixin
from functools import wraps
from typing import List

# >>>
# ... from foo import *
# ... import json
# ...
# ... with open('/tmp/tflint-output.json') as f:
# ...     tflr = json.load(f)
# >>> RAW = RawData(commit_id='a1bc', success=False, raw_data=tflr)
# >>>
# >>> import pprint as pp
# >>>
# >>> pp.pprint(RAW.generate_output())
# [{'conclusion': 'failure',
#   'head_sha': 'a1bc',
#   'name': 'TFN Linting',
#   'output': {'annotations': [{'annotation_level': 'failure',
#                               'details_url': 'https://github.com/terraform-linters/tflint/blob/v0.34.1/docs/rules/terraform_required_version.md',
#                               'end_line': 0,
#                               'message': 'terraform "required_version" '
#                                          'attribute is required',
#                               'start_line': 0,
#                               'title': 'tflint: terraform_required_version'}],
#              'summary': 'Errors occured while linting terraform files',
#              'title': 'TFN Linting'},
#   'status': 'completed',
#   'summary': 'Errors occured while linting terraform files'}]
# >>>

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@dataclass
class LintResult(JsonSchemaMixin):
    path: str
    start_line: int
    end_line: int
    start_column: int
    end_column: int
    annotation_level: str
    message: str
    title: str
    details_url: str

    @property
    def dict(self):
        d = self.to_dict()
        if d.get('start_line') and d.get('end_line'):
            if d.get('start_line') != d.get('end_line'):
                del d['start_column']
                del d['end_column']
        return d


def glr(t):
    kwargs = {}
    for k in LintResult.__annotations__.keys():
      if hasattr(t, k):
          kwargs[k] = getattr(t, k)
      else:
          kwargs[k] = None
    return LintResult(**kwargs)


def convert_annotation(func):
    @wraps(func)
    def wrapper(self):
        res = func(self)
        if hasattr(self, 'ANNOTATION_MAPPING'):
            final = self.ANNOTATION_MAPPING.get(res, res)
            return final
        return res
    return wrapper

class BaseRaw:

    def __init__(self, commit_id, success, raw_data):
        self._commit_id = commit_id
        self._success = success
        self._raw_data = raw_data

    def _conclusion_convert(self):
        if self._success is True:
            return 'success'
        return 'failure'

    @property
    def _iterator(self):
        if hasattr(self, 'iterate_key'):
            return self._raw_data[self.iterate_key]
        return self._raw_data

    def _iterate_result(self):
        results = []
        for each_result in self._iterator:
            transformer = Transformer(each_result)
            results.append(glr(transformer))
        return results

    def generate_output(self):
        flist = []
        for chunk in chunks(self._iterate_result(), 50):
            final = FinalResult(
                name = self.check_name,
                summary = self.check_summary,
                head_sha = self._commit_id,
                conclusion = self._conclusion_convert(),
                status = 'completed',
                output = FinalResultOutput(
                    title = self.check_name,
                    summary = self.check_summary,
                    text = None,
                    annotations = chunk
                )
            )
            flist.append(final.to_dict())
        return flist


@dataclass
class FinalResultOutput(JsonSchemaMixin):
    title: str
    summary: str
    text: str
    annotations: List[LintResult]


@dataclass
class FinalResult(JsonSchemaMixin):
    name: str
    head_sha: str
    summary: str
    conclusion: str
    status: str
    output: FinalResultOutput


class BaseTransformer:
    def __init__(self, raw_result):
        self._item = raw_result


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
