import os
from random import shuffle
from storage import Storage

TABLE_NAME = 'languages'

TABLE_PK = "uid"

TABLE_COLUMNS = [
    "name",
    "num_of_jobs",
    "avg_salary",
]

TABLE_ROWS = [
    ("Python", 19000, 120000, ),
    ("JavaScript", 24000, 118000, ),
    ("Java", 29000, 104000, ),
    ("C#", 18000, 97000, ),
    ("C", 8000, 97000, ),
    ("C++", 9000, 97000, ),
    ("Go", 1700, 93000, ),
    ("R", 1500, 93000, ),
    ("Swift", 1800, 93000, ),
    ("PHP", 7000, 81000, )
]


def initialize(working_dir, reset_on_exists=True):
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    storage = Storage(working_dir=working_dir)
    if storage.exists(TABLE_NAME):
        if not reset_on_exists:
            return
        os.remove(storage.path(TABLE_NAME))

    storage.create(TABLE_NAME, TABLE_PK, TABLE_COLUMNS)

    rows = TABLE_ROWS.copy()
    shuffle(rows)
    for i, row in enumerate(rows):
        cols = [(TABLE_PK, i+1)] + list(zip(TABLE_COLUMNS, row))
        storage.insert(TABLE_NAME, cols)
