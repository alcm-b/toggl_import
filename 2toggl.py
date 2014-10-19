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
    Those not mentioned in the list of supported.
"""
import csv
import fileinput
import math
import time
import string
import sys

# constants
default_starttime = '08:00:00' # harvest has no data on task start time
user_email = 'nobody@day-zero.org'
tags = 'harvest import'

# Map each Toggl column name to a function, that generates a value for that
# column. Each mapping function receives Harvest CSV row as a parameter.
field_map = {
    'Project': lambda row: fix_projectname(row),
    'Task': lambda row: row[4],
    'Description': lambda row: row[5],
    'Start date': lambda row: row[0],
    'Start time': lambda row: default_starttime,
    'Duration': lambda row: get_duration(row),
    'email': lambda row: user_email,
    'user': lambda row: '%s %s' % (row[9], row[10]),
    'tags': lambda row: tags,
    'client': lambda row: get_client(row),
}

def fix_projectname(row):
    """Change project name, depending on the name of a task."""
    if row[4] in ('bind', 'restricted'):
        id = 4
    else:
        id = 2 # Harvest project name
    return row[id]

def get_duration(harvest_row):
    """Calculate task duration."""
    hours = float(harvest_row[6])
    full_hours = math.floor(hours)
    minutes = (hours - full_hours)*60
    return '{:02n}:{:02n}:00'.format(full_hours, int(minutes))

def get_client(row):
    """Infer client name from task name, where applicable."""
    task_client = {
            'bind': 'Parallels',
            'restricted': 'Xiag'
    }
    taskname = row[4]
    if taskname in task_client:
        return task_client[taskname]
    else:
        return row[1] # client name specified in harvest

csvfile = fileinput.input()
csvrows = csv.reader(csvfile)
output = csv.writer(sys.stdout, lineterminator='\n')
csvrows.next()
header = []
for title in field_map:
    header.append(title)

output.writerow(header)
for harvest_row in csvrows:
    row = [ mapper(harvest_row) for mapper in field_map.values() ]
    output.writerow(row)

# noremap <F3> :!python % < harvest_exported.csv > toggl_import.csv <CR>
