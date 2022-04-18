from datetime import datetime

EVENTS_DICT = {
    "FileCopy": ("EventType", "md5", "TargetPath", "FileName"),
    "ExecCommand" : ("EventType", "CommandText")
}

print(str(datetime.now()).split('.')[0])