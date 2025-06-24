import caldav
from caldav.calendarobjectresource import Todo
from icalendar import Todo as IcalTodo


class DavSession:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def _get_client(self):
        if not hasattr(self, 'client'):
            self.client = caldav.DAVClient(
                url=self.url,
                username=self.username,
                password=self.password
            )
        return self.client

    def _get_calendar_urls(self):
        """Retrieve all calendar URLs from the DAV client."""
        if not hasattr(self, 'calendar_urls'):
            client = self._get_client()
            principal = client.principal()
            calendars = principal.calendars()
            self.calendar_urls = {cal.name : cal.url for cal in calendars}
        return self.calendar_urls

    def toggle_complete(self, uid, calendar):
        client = self._get_client()
        calendar_urls = self._get_calendar_urls()
        calendar = client.calendar(url=calendar_urls[calendar])
        task = calendar.todo_by_uid(uid=uid)
        assert isinstance(task, Todo), "Resource is not a Todo"
        if task:
            ical = task.icalendar_component
            completed = ical.get('status') == 'COMPLETED'
            if completed:
                task.uncomplete()
            else:
                task.complete()

        return task

    def sync(self) -> list[dict]:
        task_list = []
        calendar_urls = self._get_calendar_urls()
        client = self._get_client()
        for name, url in calendar_urls.items():
            cal = client.calendar(url=url)
            tasks = cal.todos()
            for task in tasks:
                ical : IcalTodo = task.icalendar_component
                task_dict = {
                    'ical' : ical,
                    'calendar': name,
                }
                task_list.append(task_dict)
        return task_list
