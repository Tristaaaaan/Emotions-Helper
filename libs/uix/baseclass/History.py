from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from functions.db import EmotionDatabase


class HistoryListButton(BoxLayout, Button):
    def __init__(self, **kwargs) -> None:
        super(HistoryListButton, self).__init__()


# user history
class History(BoxLayout):

    Builder.load_file('libs/uix/kv/History.kv')

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self._parent = parent
        self.load_list()

    def load_list(self):
        table_box = self.ids.row_task_box
        table_box.clear_widgets()
        db6 = EmotionDatabase()
        results = db6.get_history()
        if results:
            for i, result in enumerate(results):
                row = HistoryListButton()
                id = result[0]
                date = result[1]
                row.ids.lbl_date.text = date
                row.ids.lbl_value1.text = result[2]
                # row.bind(on_press=partial(self._parent.call_task_page, id))
                table_box.add_widget(row)
