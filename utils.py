from icalendar import Todo
from datetime import datetime

def format_date(date_value):
    date = None
    if date_value is not None:
        date = date_value.dt
        # Convert datetime to date if necessary
        if isinstance(date, datetime):
            date = date.date()

    date_str = date.strftime('%Y-%m-%d') if date else 'N/A'
    return date_str

def extract_task_details(tasks: list[dict]) -> list[dict]:
    """
    Extracts relevant details from a list of task dictionaries.
    Each task dictionary is expected to have an 'ical' key containing a
    icalendar.Todo object and a 'calendar' key with the calendar name.
    """
    extracted_tasks = []
    for task_dict in tasks:
        uid = task_dict.get('uid')
        ical_task = task_dict.get('ical')

        if not ical_task:
            continue

        summary = ical_task.get('summary', '')

        due_val = ical_task.get('due')
        due_date = None
        if due_val:
            due_date = due_val.dt
            # Convert datetime to date if necessary
            if isinstance(due_date, datetime):
                due_date = due_date.date()

        start_val = ical_task.get('dtstart')
        start_date = None
        if start_val:
            start_date = start_val.dt
            # Convert datetime to date if necessary
            if isinstance(start_date, datetime):
                start_date = start_date.date()

        status = ical_task.get('status')
        is_completed = status == 'COMPLETED'

        extracted_tasks.append({
            'uid': uid,
            'calendar': task_dict.get('calendar', 'Unknown'),
            'summary': str(summary),
            'due_date': due_date,
            'start_date': start_date,
            'completed': is_completed,
            'original_task': task_dict # For potential updates
        })
    return extracted_tasks
