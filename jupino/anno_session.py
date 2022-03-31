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
        self,
        examples: List[Example],
        labels: Union[Any, Callable[[Example], Any]],
    ):
        self.examples = examples
        self.current_example_idx = -1
        if isfunction(labels):
            self.label_getter = labels
        else:
            self.label_getter = lambda _: labels

    def get_current_example(self) -> Tuple[Optional[Example], Optional[Any]]:
        if not 0 <= self.current_example_idx < len(self.examples):
            return None, None

        example = self.examples[self.current_example_idx]
        return example, self.label_getter(example)

    def get_next_example(self) -> Tuple[Optional[Example], Optional[Any]]:
        if self.current_example_idx >= len(self.examples) - 1:
            return None, None

        self.current_example_idx += 1
        example = self.examples[self.current_example_idx]

        labels = self.label_getter(example)
        return example, labels

    def get_previous_example(self) -> Tuple[Optional[Example], Optional[Any]]:
        if self.current_example_idx <= 0:
            return None, None

        self.current_example_idx -= 1
        example = self.examples[self.current_example_idx]

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
