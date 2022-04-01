import functools
import inspect
from typing import Any, Callable, Optional, Tuple, Union

import ipywidgets as w
from jupino.interface import Example, ExampleLabelsWidgetFactory, LabelValueGetter


class FunctionBasedExampleLabelsWidgetFactory(ExampleLabelsWidgetFactory):
    def __init__(
        self,
        fn: Callable[
            [Example, Any], Union[w.Widget, Tuple[w.Widget, LabelValueGetter]]
        ],
        **fn_kwargs,
    ):
        self.fn = fn
        self.fn_kwargs = fn_kwargs
        params = inspect.signature(self.fn).parameters
        if not set(["example", "labels"]).issubset(params):
            raise ValueError("Function must accept example and labels parameters")

    def create(
        self, example: Example, labels: Any
    ) -> Optional[Tuple[w.Widget, LabelValueGetter]]:
        output = self.fn(example, labels, **self.fn_kwargs)
        if isinstance(output, w.Widget):
            if not hasattr(output, "value"):
                msg = f"The widget returned by {self.fn} does not have 'value' attribute so value_getter cannot be automatically inferred."
                msg = f"{msg}. Modify the function {self.fn} to return a tuple of widget and a callable which accepts no parameters and returns a value from the widget"
                raise ValueError(msg)

            widget, value_getter = output, lambda: getattr(output, "value")
            return widget, value_getter

        elif isinstance(output, tuple):
            widget, value_getter = output
            if not inspect.isfunction(value_getter):
                raise ValueError(
                    f"Second item of tuple returned by {self.fn} must be a callable which accepts no parameters and returns value of the widget"
                )
            return widget, value_getter
        else:
            msg = f"Function {self.fn} that creates label widget must (example, labels) as parameters and return"
            msg = f"{msg} either a Jupyter widget or a tuple of Jupyter widget and a callable that takes no argument and returns the value of this widget"
            raise ValueError(msg)


def label_widget(f) -> Callable[..., FunctionBasedExampleLabelsWidgetFactory]:
    @functools.wraps(f)
    def factory(**kwargs: Any):
        return FunctionBasedExampleLabelsWidgetFactory(fn=f, **kwargs)

    return factory


@label_widget
def toggle_buttons(example: Example, labels: Any, **kwargs):
    return w.ToggleButtons(options=labels, value=example.y, **kwargs)


@label_widget
def select_multiple(example: Example, labels: Any, **kwargs):
    return w.SelectMultiple(
        options=labels, value=list(example.y) if example.y else [], **kwargs
    )


@label_widget
def dropdown(example: Example, labels: Any, **kwargs):
    return w.Dropdown(options=labels, value=example.y, **kwargs)


@label_widget
def radio_button(example: Example, labels: Any, **kwargs):
    return w.RadioButtons(options=labels, value=example.y, **kwargs)
