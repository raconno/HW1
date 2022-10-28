from collections import defaultdict, Counter
from functools import reduce
import datetime
import json
import os

file = open('data.jsonl', 'r', encoding='utf-8')


class User:  # create class to use set feature(ignore non-unique object)
    def __init__(self, dictionary):
        self.info = dictionary

    def __members(self):  # create centralized method to easily change key properties
        return self.info['name'], self.info['time_created']

    def __eq__(self, other):  # check equality by name and time of creation
        if type(other) is type(self):
            return self.__members() == other.__members()
        else:
            return False

    def __hash__(self):  # change hash func in accordance with equal func
        return hash(self.__members())

    def complement(self, default_values):  # staff user with missing fields
        info = self.info
        renovated_info = {}  # create new dictionary to have the same order of fields
        info['time_created'] = int(info['time_created'].timestamp())  # convert datetime object to int timestamp
        for key, value in default_values.items():  # go through all required fields
            if not info.get(key):  # if user have such field remain it
                renovated_info[key] = value
            else:  # if user does not add it with default value
                renovated_info[key] = info[key]
        return renovated_info  # send only data dictionary


users = set()  # set of objects type User
for user_json in file:
    user = User(json.loads(user_json))  # convert json line to dict and assign to user`s info
    # convert time stamp to datetime object
    user.info['time_created'] = datetime.datetime.fromtimestamp(user.info['time_created'])
    users.add(user)  # eliminate duplicates
file.close()

properties = defaultdict(list)  # dictionary of all keys with lists of all not None values
for user in users:
    for key in user.info.keys():  # go through all keys of all users
        # add user`s property (if it has value) in list of appropriate key
        properties[key].append(user.info[key]) if user.info[key] is not None else None

default_values = {}  # dictionary of all keys with default values according to task
for key, value in properties.items():  # iterate through all possible keys
    if isinstance(key, bool):  # firstly check bool to not handle with as int
        default_values[key] = None
    elif isinstance(key, int):
        # get average and round the amount down
        default_values[key] = int(reduce(lambda x, y: x + y, value) / len(value))
    elif isinstance(key, float):
        default_values[key] = reduce(lambda x, y: x + y, value) / len(value)  # get average
    elif isinstance(key, str):
        default_values[key] = Counter(value).most_common(1)[0][0]  # get most common
    else:
        default_values[key] = None

prepared_to_json_users = defaultdict(list)  # dictionary of '{year}-{month}-{day}' with matching user`s infos
for user in users:
    date = user.info['time_created']  # get the time of creation of user
    key = str(date.year) + '-' + str(date.month) + '-' + str(date.day)  # and generate user`s filename
    prepared_to_json_users[key].append(user.complement(default_values))  # add complemented user to appropriate file

for key, _ in prepared_to_json_users.items():  # delete previous files
    try:
        os.remove(str(key) + ".jsonl")
    except:
        pass

for key, value in prepared_to_json_users.items():
    with open(str(key) + ".jsonl", "x") as file:  # create file
        for user in value:
            file.write('\n' + json.dumps(user))  # add users to file enter-separated
