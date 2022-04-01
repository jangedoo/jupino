import functools
from typing import Callable, List, Optional, Union

import ipywidgets as w
from jupino.anno_session import Example
from jupino.interface import ExampleXWidgetFactory


class FunctionBasedExampleXWidgetFactory(ExampleXWidgetFactory):
    def __init__(self, fn: Callable[[Example], w.Widget], **kwargs):
        self.fn = fn
        self.kwargs = kwargs

    def create(self, example: Example) -> Optional[w.Widget]:
        return self.fn(example, **self.kwargs)


def x_widget(f) -> Callable[..., FunctionBasedExampleXWidgetFactory]:
    @functools.wraps(f)
    def factory(**kwargs):
        return FunctionBasedExampleXWidgetFactory(fn=f, **kwargs)

    return factory


@x_widget
def html(example: Example):
    return w.HTML(value=f"{example.x}")


@x_widget
def image(example: Example, width=300, height=300, **kwargs):
    if isinstance(example.x, str):
        with open(example.x, "rb") as f:
            image = f.read()
    else:
        image = example.x
    return w.Image(value=image, width=width, height=height, **kwargs)


@x_widget
def multiple(
    example: Example,
    factories: Union[ExampleXWidgetFactory, List[ExampleXWidgetFactory]],
    vertical_layout=False,
):
    if isinstance(factories, ExampleXWidgetFactory):
        factories = [factories] * len(example.x)

    if len(example.x) != len(factories):
        raise ValueError(
            "Number of items in x should be same as number of factories provided"
        )

    clones = [Example(x=x, y=example.y) for x in example.x]
    children = [f.create(ex) for f, ex in zip(factories, clones)]

    if vertical_layout:
        return w.VBox(children=children)
    else:
        return w.HBox(children=children)
