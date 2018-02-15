from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import

from collections import defaultdict

import datetime
import glob
import json
import os
import re


def _read_json_dict(filename, key='id'):
    with open(filename) as fin:
        records = json.load(fin)
        json_dict = {
            record[key]: record
            for record in records
        }
    return json_dict


class SlackLoader(object):
    def __init__(self, export_path, exclude_channels=(), only_channels=(), start_date=None, end_date=None,
                 is_sorted=True):
        self.exclude_channels = exclude_channels
        self.only_channels = only_channels
        if start_date:
            self.start_date = (start_date - datetime.datetime(1970, 1, 1)).total_seconds()
        else:
            self.start_date = None
        if end_date:
            self.end_date = (end_date - datetime.datetime(1970, 1, 1)).total_seconds()
        else:
            self.end_date = None
        self.channels = _read_json_dict(os.path.join(export_path, 'channels.json'))
        self.users = _read_json_dict(os.path.join(export_path, 'users.json'))
        self.messages = self.load_export(export_path, is_sorted)

    def load_export(self, export_path, is_sorted):
        messages = []
        for channel_id, channel in self.channels.items():
            if channel['is_archived']:
                continue
            if channel['name'] in self.exclude_channels:
                continue
            if self.only_channels and channel['name'] not in self.only_channels:
                continue
            messages_glob = os.path.join(export_path, channel['name'], '*.json')
            for messages_filename in glob.glob(messages_glob):
                with open(messages_filename) as f_messages:
                    for record in json.load(f_messages):
                        if 'subtype' in record:
                            continue
                        if 'ts' in record:
                            if self.start_date and float(record['ts']) < self.start_date:
                                continue
                            if self.end_date and float(record['ts']) > self.end_date:
                                continue
                            record['ts'] = float(record['ts'])
                            record['dt'] = datetime.datetime.fromtimestamp(record['ts'])
                        record['channel'] = channel_id
                        messages.append(record)
        if is_sorted:
            messages = sorted(messages, key=lambda x: x['ts'])

        return messages

    def find_threads(self):
        dd = defaultdict(list)
        for i in range(0, len(self.messages)):
            msg = self.messages[i]
            if "thread_ts" in msg:
                dd[msg["thread_ts"]].append(i)
        return list(dd.values())

re_slack_link = re.compile(r'(?P<all><(?P<id>[^\|]*)(\|(?P<title>[^>]*))?>)')


def _extract_slack_link_id(m):
    return m.group('id')


def normalize_links(text):
    return re_slack_link.sub(_extract_slack_link_id, text)


if __name__ == '__main__':
    loader = SlackLoader('ODS_dump_Mar_10_2017', exclude_channels=['_random_flood', 'career'])
    print(len(loader.messages))
