import os
from functools import wraps


UNCOMMON_EXTENSIONS = [
        '.tar'
        ]


def retrieve_extension(filename):
    for ext in UNCOMMON_EXTENSIONS:
        if ext in filename:
            index = filename.find(ext)
            return filename[index:]
    return os.path.splitext(filename)[1]


def human_readable(func):
    """Decorator that converts a number of bytes to
    a human readable format
    """
    @wraps(func)
    def wrapper(self):
        num_bytes = func(self)
        suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
        suffixIndex = 0
        while num_bytes > 1024 and suffixIndex < 5:
            suffixIndex += 1
            num_bytes = num_bytes/1024
        final_suffix = suffixes[suffixIndex]
        return f'{num_bytes:.2f} {suffixes[suffixIndex]}'
    return wrapper




