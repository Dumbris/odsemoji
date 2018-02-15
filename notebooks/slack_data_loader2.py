import datetime
import json
import os
import re
from pathlib import Path
from collections import defaultdict


re_slack_link = re.compile(r'(?P<all><(?P<id>[^\|]*)(\|(?P<title>[^>]*))?>)')

def _read_json_dict(filename, key='id'):
    with open(filename) as fin:
        records = json.load(fin)
        json_dict = {
            record[key]: record
            for record in records
        }
    return json_dict


class SlackLoader2:

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

    def get_reactions(self, msg):
        if msg['type'] == 'message' and msg.get('subtype') is None:
            msg_reacts = {}
            #react_texts.append(normalize_links(msg['text']))
            for record in msg.get('reactions', []):
                msg_reacts[record['name']] = record['count']
            return msg_reacts
        return None


    def load_export(self, export_path, is_sorted=True):
        """
                1) Link to parent message:
              "thread_ts": "1517643521.000001",
                "parent_user_id": "U1UNFRQ1K",
                2) attachments[].text
        """
        messages = []
        ref_to_id = {}
        for channel_id, channel in self.channels.items():
            #if channel['is_archived']:
            #    continue
            if channel['name'] in self.exclude_channels:
                continue
            if self.only_channels and channel['name'] not in self.only_channels:
                continue
            messages_glob = BASE_DIR / Path(channel['name'])
            for messages_filename in messages_glob.glob('*.json'):
                with open(str(messages_filename)) as f_messages:
                    for record in json.load(f_messages):
                        if 'ts' in record:
                            if self.start_date and float(record['ts']) < self.start_date:
                                continue
                            if self.end_date and float(record['ts']) > self.end_date:
                                continue
                            record['ts'] = float(record['ts'])
                            record['dt'] = datetime.datetime.fromtimestamp(record['ts'])
                        record['channel'] = channel_id
                        if 'reactions' in record:
                            record['reactions_'] = self.get_reactions(record)
                        messages.append(record)
        if is_sorted:
            messages = sorted(messages, key=lambda x: x['ts'])
        return messages

    def find_threads(self):
        dd = defaultdict(list)
        for i in range(0, len(self.messages)):
            msg = self.messages[i]
            if "thread_ts" in msg:
                key = (msg["channel"], msg["thread_ts"])
                dd[key].append(i)
        return dd
        #return list(dd.values())

    def rip_threads(self, thread_index):
        threads = []
        for i in range(0, len(self.messages)):
            msg = self.messages[i]
            key = (msg["channel"], msg["ts"])
            for submsg_index in thread_index[key]:
                submsg = self.messages[submsg_index]




def _extract_slack_link_id(m):
    return m.group('id')


def normalize_links(text):
    return re_slack_link.sub(_extract_slack_link_id, text)


if __name__ == '__main__':
    dir = '../input/export_Feb_8_2018'
    BASE_DIR = Path("/home/algis/repos/personal/MOOC/ODS_dump/input/export_Feb_8_2018")

    loader = SlackLoader2(dir, exclude_channels=['_random_flood', 'career'])
    print(len(loader.messages))
    threads = loader.find_threads()
    type(threads)
