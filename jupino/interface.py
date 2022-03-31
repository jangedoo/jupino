from dataclasses import dataclass
from typing import Any, Callable, Optional, Tuple

import ipywidgets as w

from jupino.anno_session import AnnotationSession, Example

LabelValueGetter = Callable[[], Any]


class ExampleXWidgetFactory:
    def create(self, example: Example) -> Optional[w.Widget]:
        raise NotImplementedError


class ExampleLabelsWidgetFactory:
    def create(
        self, example: Example, labels: Any
    ) -> Optional[Tuple[w.Widget, LabelValueGetter]]:
        raise NotImplementedError


class ExampleWidgetFactory:
    def create(
        self, example: Example, labels: Any
    ) -> Tuple[w.Widget, LabelValueGetter]:
        raise NotImplementedError


class SummaryWidgetFactory:
    def create(self, session: AnnotationSession) -> w.Widget:
        raise NotImplementedError


@dataclass
class ControlWidgetEvent:
    sender: w.Widget
    event_name: str


class ControlsEventHandler:
    def __init__(
        self,
        session: AnnotationSession,
        display_example: Callable[
            [Optional[Example], Any], Optional[Tuple[Example, LabelValueGetter]]
        ],
    ):
        self.session = session
        self.display_example = display_example


class ControlsWidgetFactory:
    def create(
        self, session: AnnotationSession, event_handler: ControlsEventHandler
    ) -> Tuple[w.Widget, ControlWidgetEvent]:
        raise NotImplementedError
