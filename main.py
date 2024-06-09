from nicegui import ui
import json as jsonlib
import sqlite3
import nicegui


class App():
    def __init__(self):
        self.knowledge_panel = None
        self.db = sqlite3.connect('knowledge.db')
        self.curser = self.db.cursor()
        self.curser.execute('CREATE TABLE IF NOT EXISTS knowledge (label TEXT, content TEXT UNIQUE)')
        self.curser.execute('CREATE TABLE IF NOT EXISTS labels (label TEXT)')

        with ui.row():
            self.logo = ui.avatar('🤗', text_color='grey-11', square=True)
            self.title = ui.label("HuggingUI")

        with ui.tabs().classes('w-full') as tabs:
            ui.tab('Knowledge', icon='school')
            ui.tab('Create', icon='create')
            ui.tab('Upload', icon='upload')

        with ui.tab_panels(tabs, value='Create').classes('w-full'):
            ui.update()
            self.knowledge_panel = ui.tab_panel('Knowledge')
            with self.knowledge_panel:
                for row in self.curser.execute('SELECT * FROM knowledge'):
                    with ui.expansion(row[1]):
                        ui.label(row[0])
            with ui.tab_panel('Create'):
                self.content_input = ui.input(label='Content')
                self.label_input = ui.input(label='Label')
                self.submit = ui.button('Submit', on_click=self.submit)
            with ui.tab_panel('Upload'):
                self.uploader = ui.upload(auto_upload=True, on_upload=self.upload, label='Upload JSONL')

    def submit(self):
        if self.content_input.value and self.label_input.value:
            try:
                self.curser.execute('INSERT INTO knowledge (label, content) VALUES (?, ?)', (self.label_input.value,
                                                                                             self.content_input.value))
                self.db.commit()
                self.knowledge_panel.default_slot.append( ui.expansion(self.content_input.value).default_slot.children.append(ui.label(self.label_input.value)))

                self.content_input.value = ''
                self.label_input.value = ''
            except sqlite3.IntegrityError:
                ui.notify('This content already exists.')
        else:
            ui.notify('Please fill out both fields.')

    def upload(self, file: nicegui.elements.upload.UploadEventArguments):
        if file.name.split(".")[1] == 'jsonl':
            try:
                contents = list(file.content)
                for json in contents:
                    valid_json = jsonlib.loads(json)
                    self.curser.execute('INSERT INTO knowledge (label, content) VALUES (?, ?)', (valid_json['label'],
                                                                                                 valid_json['content']))
                self.db.commit()
            except jsonlib.JSONDecodeError:
                ui.notify('Invalid JSONL file')
            except KeyError:
                ui.notify('The proper keys could not be found.')
        else:
            ui.notify('Invalid file type')

    def start(self):
        ui.run()


app = App()
ui.run()
