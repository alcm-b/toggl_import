#!/usr/bin/python
"""
Convert Harvest CSV files to the format, that Toggl can import.

Example:
    $ python 2toggl.py < harvest_exported.csv > toggl_import.csv

Harvest column names, this script expects as input:
    Date, Client, Project, Project Code, Task, Notes, Hours, Billable?,
    Invoiced?, First Name,Last Name,Department,Employee?,Hourly Rate,Billable
    Amount,Currency

Supported Toggl columns:
    Project, Task, Description, Start date, Start time, Duration, Email, User,
    tags, client

Unsupported Toggl columns:
    The rest of them: those not listed as supported.
"""
import csv
import fileinput
import math
import string
import sys
import time

# constants
default_starttime = '08:00:00' # harvest has no data on task start time
user_email = 'nobody@example.com'
tags = 'harvest import'

# extra mapping
task_to_projectname = () # ('bind', 'restricted')
task_client = {} # { 'bind': 'Parallels', 'restricted': 'Xiag' }

# Map each Toggl column name to a function, that generates a value for that
# column. Each mapping function receives Harvest CSV row as a parameter.
field_map = {
    'Project': lambda row: fix_projectname(row, task_to_projectname),
    'Task': lambda row: row[4],
    'Description': lambda row: row[5],
    'Start date': lambda row: row[0],
    'Start time': lambda row: default_starttime,
    'Duration': lambda row: get_duration(row),
    'email': lambda row: user_email,
    'user': lambda row: '%s %s' % (row[9], row[10]),
    'tags': lambda row: tags,
    'client': lambda row: get_client(row, task_client),
}

def fix_projectname(row, task_to_projectname):
    """Change project name, depending on the name of a task."""
    if row[4] in task_to_projectname:
        id = 4 # Harvest task name
    else:
        id = 2 # Harvest project name
    return row[id]

def get_duration(harvest_row):
    """Calculate task duration."""
    hours = float(harvest_row[6])
    full_hours = math.floor(hours)
    minutes = (hours - full_hours)*60
    return '{:02n}:{:02n}:00'.format(full_hours, int(minutes))

def get_client(row, task_client):
    """Infer client name from task name, where applicable."""
    taskname = row[4]
    if taskname in task_client:
        return task_client[taskname]
    else:
        return row[1] # client name specified in harvest

csvfile = fileinput.input()
csvrows = csv.reader(csvfile)
output = csv.writer(sys.stdout, lineterminator='\n')
csvrows.next() # skip header
header = field_map.keys()
output.writerow(header)
for harvest_row in csvrows:
    row = [ mapper(harvest_row) for mapper in field_map.values() ]
    output.writerow(row)

# noremap <F3> :!python % < harvest_exported.csv > toggl_import.csv <CR>
