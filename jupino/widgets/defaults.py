import inspect
from typing import Any, Callable, Optional, Tuple

import ipywidgets as w
from IPython.display import display
from jupino.anno_session import AnnotationSession, Example
from jupino.interface import (
    ControlsEventHandler,
    ControlsWidgetFactory,
    ControlWidgetEvent,
    ExampleLabelsWidgetFactory,
    ExampleWidgetFactory,
    ExampleXWidgetFactory,
    LabelValueGetter,
    SummaryWidgetFactory,
)
from jupino.widgets.labels import dropdown, label_widget, toggle_buttons
from jupino.widgets.x import x_widget


class DefaultExampleXWidgetFactory(ExampleXWidgetFactory):
    def create(self, example: Example) -> Optional[w.Widget]:
        return w.HTML(value=f"{example.x}")


class DefaultExampleLabelsWidgetFactory(ExampleLabelsWidgetFactory):
    def __init__(self, multi_choice: bool = False):
        self.multi_choice = multi_choice

    def create(
        self, example: Example, labels: Any
    ) -> Optional[Tuple[w.Widget, LabelValueGetter]]:
        if len(labels) <= 10:
            return toggle_buttons().create(example, labels)
        else:
            return dropdown().create(example, labels)


class DefaultExampleWidgetFactory(ExampleWidgetFactory):
    def __init__(
        self,
        x_widget_factory: ExampleXWidgetFactory,
        labels_widget_factory: ExampleLabelsWidgetFactory,
    ):
        self.example_x_widget_factory = x_widget_factory
        self.example_labels_widget_factory = labels_widget_factory

    def create(
        self, example: Example, labels: Any
    ) -> Tuple[w.Widget, LabelValueGetter]:
        x_widget = self.example_x_widget_factory.create(example=example)
        labels_widget_and_value_getter = self.example_labels_widget_factory.create(
            example=example, labels=labels
        )

        if labels_widget_and_value_getter is None:
            raise Exception(
                f"No widgets were created for Labels for example {example} and labels {labels}"
            )
        if not isinstance(labels_widget_and_value_getter, tuple):
            raise Exception(
                "Labels widget must return a tuple with elements: widget and a callable that takes no arguments and returns a value"
            )

        labels_widget, value_getter = labels_widget_and_value_getter

        ui_children = []
        if x_widget:
            ui_children.append(x_widget)
        ui_children.append(w.HTML(value="<hr>"))
        ui_children.append(labels_widget)
        return w.VBox(children=ui_children), value_getter


class DefaultSummaryWidgetFactory(SummaryWidgetFactory):
    def create(self, session: AnnotationSession) -> w.Widget:
        return w.HBox(
            children=[
                w.Label(value=f"Current example: {session.current_example_idx + 1}"),
                w.IntProgress(
                    value=session.total_annotated_examples,
                    min=0,
                    max=session.total_examples,
                    description="Progress",
                    orientation="horizontal",
                    bar_style="info",
                ),
                w.Label(
                    value=f"Annotated: {session.total_annotated_examples} / {session.total_examples}"
                ),
            ]
        )


class DefaultControlsEventHandler(ControlsEventHandler):
    def __init__(
        self,
        session: AnnotationSession,
        display_example: Callable[
            [Optional[Example], Any], Optional[Tuple[Example, LabelValueGetter]]
        ],
    ):
        super().__init__(session=session, display_example=display_example)
        self.current_example_annotation_getter: Optional[
            Tuple[Example, LabelValueGetter]
        ] = None

        # settings
        self.auto_submit = True

    def save_annotation(self):
        if self.current_example_annotation_getter is None:
            return

        example, value_getter = self.current_example_annotation_getter
        example.y = value_getter()

    def on_submit(self, event: ControlWidgetEvent):
        self.save_annotation()

        example, labels = self.session.get_current_example()
        self._trigger_display(example=example, labels=labels)

    def _trigger_display(self, example: Optional[Example], labels: Any):
        self.current_example_annotation_getter = self.display_example(example, labels)

    def on_next(self, event: ControlWidgetEvent):
        if self.auto_submit:
            self.save_annotation()

        example, labels = self.session.get_next_example()
        self._trigger_display(example=example, labels=labels)

    def on_previous(self, event: ControlWidgetEvent):
        example, labels = self.session.get_previous_example()
        self._trigger_display(example=example, labels=labels)

    def on_auto_submit(self, event: ControlWidgetEvent):
        self.auto_submit = event.event_name == "enable_auto_submit"


class DefaultControlsWidgetFactory(ControlsWidgetFactory):
    def create(
        self,
        session: AnnotationSession,
        event_handler: DefaultControlsEventHandler,
    ) -> w.Widget:

        btn_next = w.Button(description="Next >>")
        btn_next.on_click(
            lambda _: event_handler.on_next(
                ControlWidgetEvent(event_name="next", sender=btn_next)
            )
        )
        btn_previous = w.Button(description="<< Previous")
        btn_previous.on_click(
            lambda _: event_handler.on_previous(
                ControlWidgetEvent(event_name="previous", sender=btn_previous)
            )
        )

        btn_submit = w.Button(description="Submit", button_style="primary")
        btn_submit.on_click(
            lambda _: event_handler.on_submit(
                ControlWidgetEvent(event_name="submit", sender=btn_submit)
            )
        )

        chk_auto_submit = w.Checkbox(description="Auto submit on Next?", value=True)

        def chk_callback(change):
            if change.get("name") != "value":
                return

            event_name = (
                "enable_auto_submit"
                if change.get("new", False) == True
                else "disable_auto_submit"
            )
            event_handler.on_auto_submit(
                ControlWidgetEvent(event_name=event_name, sender=chk_auto_submit)
            )

        chk_auto_submit.observe(chk_callback)

        return w.HBox(children=[btn_previous, btn_next, btn_submit, chk_auto_submit])


class AnnotationSessionWidget:
    def __init__(
        self,
        session: AnnotationSession,
        controls_widget_factory: Optional[ControlsWidgetFactory] = None,
        controls_event_handler: Optional[ControlsEventHandler] = None,
        example_widget_factory: Optional[ExampleWidgetFactory] = None,
        summary_widget_factory: Optional[SummaryWidgetFactory] = None,
    ):
        self.session = session

        if controls_widget_factory is None:
            self.controls_widget_factory = DefaultControlsWidgetFactory()
            self.controls_event_handler = DefaultControlsEventHandler(
                session=self.session,
                display_example=self._display_example,
            )
        elif controls_widget_factory is not None and controls_event_handler is not None:
            self.controls_widget_factory = controls_widget_factory
            self.controls_event_handler = controls_event_handler
        else:
            raise ValueError(
                "controls_event_handler must be passwed when controls_widget_factor is also given"
            )

        self.example_widget_factory = (
            example_widget_factory
            or DefaultExampleWidgetFactory(
                x_widget_factory=DefaultExampleXWidgetFactory(),
                labels_widget_factory=DefaultExampleLabelsWidgetFactory(),
            )
        )
        self.summary_widget_factory = (
            summary_widget_factory or DefaultSummaryWidgetFactory()
        )

        self.controls_out = w.Output()
        self.example_out = w.Output()
        self.summary_out = w.Output()

    def _display_example(
        self, example: Optional[Example], labels: Any
    ) -> Optional[Tuple[Example, LabelValueGetter]]:

        with self.summary_out:
            self.summary_out.clear_output(wait=False)
            summary_widget = self.summary_widget_factory.create(session=self.session)
            display(summary_widget)

        if example is None:
            with self.example_out:
                self.example_out.clear_output()
                display(w.Label(value="Nothing to show :)"))
                return None

        example_widget, value_getter = self.example_widget_factory.create(
            example=example, labels=labels
        )

        with self.example_out:
            self.example_out.clear_output(wait=False)
            display(example_widget)

        return example, value_getter

    def display(self):
        with self.summary_out:
            self.summary_out.clear_output(wait=False)
            summary_widget = self.summary_widget_factory.create(session=self.session)
            display(summary_widget)

        with self.example_out:
            self.example_out.clear_output(wait=False)
            display(w.Label(value="Click Next to start annotating"))

        with self.controls_out:
            self.controls_out.clear_output(wait=False)
            controls_widget = self.controls_widget_factory.create(
                session=self.session,
                event_handler=self.controls_event_handler,
            )
            display(controls_widget)

        # layout factory can be used here
        display(
            w.VBox(children=[self.summary_out, self.example_out, self.controls_out])
        )

    def _ipython_display_(self):
        self.display()


def annotate(
    examples: list,
    labels: Any,
    x_widget_factory: Optional[ExampleXWidgetFactory] = None,
    labels_widget_factory: Optional[ExampleLabelsWidgetFactory] = None,
    example_widget_factory: Optional[ExampleWidgetFactory] = None,
    summary_widget_factory: Optional[SummaryWidgetFactory] = None,
    controls_widget_factory: Optional[ControlsWidgetFactory] = None,
    controls_event_handler: Optional[DefaultControlsEventHandler] = None,
) -> AnnotationSessionWidget:
    if not isinstance(examples, list):
        examples = list(examples)

    if len(examples) == 0:
        raise ValueError("There must be atleast one item in examples")

    if not isinstance(examples[0], Example):
        examples = [Example(x=e) for e in examples]

    sess = AnnotationSession(examples=examples, labels=labels)

    if x_widget_factory and inspect.isfunction(x_widget_factory):
        x_widget_factory = x_widget(x_widget_factory)()

    if labels_widget_factory and inspect.isfunction(labels_widget_factory):
        labels_widget_factory = label_widget(labels_widget_factory)()

    # if example widget factory is not given but one of x_widget_factory or labels_widget_factory
    # is given then create an ExampleWidgetFactory using those
    if example_widget_factory is None and (x_widget_factory or labels_widget_factory):
        example_widget_factory = DefaultExampleWidgetFactory(
            x_widget_factory=x_widget_factory or DefaultExampleXWidgetFactory(),
            labels_widget_factory=labels_widget_factory
            or DefaultExampleLabelsWidgetFactory(),
        )

    sess_widget = AnnotationSessionWidget(
        session=sess,
        controls_widget_factory=controls_widget_factory,
        controls_event_handler=controls_event_handler,
        example_widget_factory=example_widget_factory,
        summary_widget_factory=summary_widget_factory,
    )
    return sess_widget
