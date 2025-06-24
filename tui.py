from textual.app import App, ComposeResult
from textual.containers import Container
from textual.coordinate import Coordinate
from textual.widgets import DataTable, Footer, Header

from dav import DavSession
from utils import format_date


class TasksApp(App):
    """A Textual app to manage tasks."""

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
        ("m", "toggle_task_complete", "Toggle Complete"),
    ]

    def __init__(self, tasks, dav_session, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = tasks
        self.dav_session : DavSession = dav_session

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(DataTable(id="tasks_table", cursor_type="row"), id="tasks_container")
        yield Footer()

    def parse_taks(self, ical_task):


        uid = ical_task.get('uid')
        summary = ical_task.get('summary', '')
        start_date = format_date(ical_task.get('dtstart'))
        due_date = format_date(ical_task.get('due'))
        status = "[✗]" if ical_task.get('completed') else "[ ]"
        return uid, summary, start_date, due_date, status

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        table = self.query_one(DataTable)
        table.add_columns("Completed", "Summary", "Start", "Due", "Calendar")

        for task in self.tasks:
            ical_task = task.get('ical')
            if not ical_task:
                continue
            else:
                uid, summary, start_date, due_date, status = self.parse_taks(ical_task)
                table.add_row(
                    status,
                    summary,
                    start_date,
                    due_date,
                    task['calendar'],
                    key=uid # A unique key for the row
                )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def action_toggle_task_complete(self) -> None:
        """An action to toggle the completeness of the selected task."""
        table = self.query_one(DataTable)
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        row_idx = table.cursor_row
        _, _, _, _, cal = table.get_row(row_key)
        task = self.dav_session.toggle_complete(row_key.value, cal)
        _, _, _, _, status = self.parse_taks(task.icalendar_component)
        table.update_cell_at(Coordinate(row_idx, 0), status)

        #print(f"Toggling task completeness for row key: {row_key}")


        # You will add your logic here to update the task's completeness
        # using the row_key (which is the task's UID)

def run_tui(tasks, dav_session):
    """Run the TUI application."""
    app = TasksApp(tasks=tasks, dav_session=dav_session)
    app.run()
