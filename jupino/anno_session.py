from dataclasses import dataclass
from inspect import isfunction
from typing import Any, Callable, List, Optional, Tuple, Union


@dataclass
class Example:
    x: Any
    y: Optional[Any] = None

    @property
    def is_annotated(self) -> bool:
        return self.y is not None


class AnnotationSession:
    def __init__(
        self, examples: List[Example], labels: Union[Any, Callable[[Example], Any]]
    ):
        self.examples = examples
        self._examples_iter = iter(self.examples)
        if isfunction(labels):
            self.label_getter = labels
        else:
            self.label_getter = lambda _: labels

    def get_next_example(self) -> Optional[Tuple[Example, Any]]:
        example = next(self._examples_iter, None)
        if example is None:
            return None

        labels = self.label_getter(example)
        return example, labels

    @property
    def annotated_examples(self):
        return [e for e in self.examples if e.is_annotated]

    @property
    def unannotated_examples(self):
        return [e for e in self.examples if not e.is_annotated]

    @property
    def total_examples(self):
        return len(self.examples)

    @property
    def total_unannotated_examples(self):
        return len(self.unannotated_examples)

    @property
    def total_annotated_examples(self):
        return len(self.annotated_examples)
