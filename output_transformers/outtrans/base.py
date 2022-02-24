import inspect
from dataclasses import dataclass
from dataclasses_jsonschema import JsonSchemaMixin
from functools import wraps
from typing import List


def get_transform_modules(downstream):
    modules = {}
    for mn, m in inspect.getmembers(downstream, predicate=inspect.ismodule):
        modules[f".{mn}"] = m
    return modules


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

def generate_generic_error_markdown(lint_issues):
    markdown = "\n\n## Generic errors that couldn't be associated with a file.\n"
    for issue in lint_issues:
        markdown += f"### {issue.title}\n`{issue.message}`\n[See here for details]({issue.details_url})\n\n"
    return markdown


class BaseRaw:

    def __init__(self, commit_id, success, raw_data, transformer_cls):
        self._commit_id = commit_id
        self._success = success
        self._raw_data = raw_data
        self._tcls = transformer_cls

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
            transformer = self._tcls(each_result)
            results.append(glr(transformer))
        return results

    def generate_output(self):
        flist = []
        generic = []
        specific = []
    
        for _ir in self._iterate_result():
            if not _ir.path:
                generic.append(_ir)
            else:
                specific.append(_ir)

        text_markdown = generate_generic_error_markdown(generic) if generic else None

        for chunk in chunks(specific, 50):
            final = FinalResult(
                name = self.check_name,
                summary = self.check_summary,
                head_sha = self._commit_id,
                conclusion = self._conclusion_convert(),
                status = 'completed',
                output = FinalResultOutput(
                    title = self.check_name,
                    summary = self.check_summary,
                    text = text_markdown,
                    annotations = chunk
                )
            )
            flist.append(final.to_dict(omit_none=True))

        if not flist:
            final = FinalResult(
                name = self.check_name,
                summary = self.check_summary,
                head_sha = self._commit_id,
                conclusion = self._conclusion_convert(),
                status = 'completed',
                output = FinalResultOutput(
                    title = self.check_name,
                    summary = self.check_summary,
                    text = text_markdown,
                    annotations = None
                )
            )
            flist.append(final.to_dict(omit_none=True))

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

