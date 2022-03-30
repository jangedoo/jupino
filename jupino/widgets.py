import ipywidgets as w

from jupino.anno_session import AnnotationSession, Example


class AnnotationSessionWidget:
    def __init__(self, session: AnnotationSession):
        self.session = session
        self.controls_widget_factory = controls_widget_factory
        self.example_widget_factory = example_widget_factory
        self.summary_widget_factory = summary_widget_factory
        self.layout_widget_factory = layout_widget_factory

        self.controls_out = w.Output()
        self.example_out = w.Output()
        self.summary_out = w.Output()
        self.layout_out = w.Output()

    def display_example(self, example: Example):
        pass

    def display(self):
        with self.controls_out:
            pass
