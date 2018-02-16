import datetime
import json
import os
import re
from pathlib import Path
from collections import defaultdict
import copy
import tqdm


re_slack_link = re.compile(r'(?P<all><(?P<id>[^\|]*)(\|(?P<title>[^>]*))?>)')

def _read_json_dict(filename, key='id'):
    with open(filename) as fin:
        records = json.load(fin)
        json_dict = {
            record[key]: record
            for record in records
        }
    return json_dict


EOU_TOKEN = "__eou__"


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
        self.channels = _read_json_dict(os.path.join(str(export_path), 'channels.json'))
        self.users = _read_json_dict(os.path.join(str(export_path), 'users.json'))
        self.messages = self.load_export(export_path, is_sorted)
        self.threads_index = None
        self.threads = None
        self.index_threads()
        self.rip_threads()

    @staticmethod
    def get_reactions(msg):
        if msg['type'] == 'message' and msg.get('subtype') is None:
            msg_reacts = {}
            #react_texts.append(normalize_links(msg['text']))
            for record in msg.get('reactions', []):
                msg_reacts[record['name']] = record['count']
            return msg_reacts if len(msg_reacts) > 0 else None
        return None

    @staticmethod
    def key_str(key):
        return str(key[0]) + "/" + str(key[1])

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
            messages_glob = export_path / Path(channel['name'])
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

    def index_threads(self):
        dd = defaultdict(list)
        for i in range(0, len(self.messages)):
            msg = self.messages[i]
            if "thread_ts" in msg:
                key = (msg["channel"], msg["thread_ts"])
                dd[self.key_str(key)].append(i)
        self.threads_index = dd

    def get_text(self, msg):
        keys = ["text", "plain_text"]
        att_keys = ["text", "more"]
        text = None
        for key in keys:
            if (key in msg) and msg[key] and (len(msg[key]) > 0):
                text = msg[key]
                break
        if "attachments" in msg:
            att_texts = []
            for att in msg["attachments"]:
                for att_key in att_keys:
                    if (att_key in att) and att[att_key] and (len(att[att_key]) > 0):
                        att_texts.append(att[att_key] + EOU_TOKEN)
            if not text:
                text = " ".join(att_texts)
            else:
                text += " ".join(att_texts)
        return text

    def rip_threads(self):
        processed_ids = []
        if not self.threads:
            self.threads = []
        for i in tqdm.tqdm(range(0, len(self.messages))):
            if i in processed_ids:
                continue
            msg = self.messages[i]
            if "text" not in msg:
                continue
            thread = {}

            key = (msg["channel"], msg["ts"])
            thread["key"] = key

            text = self.get_text(msg)
            if text:
                thread["text"] = " ".join([text, EOU_TOKEN])
            else:
                thread["text"] = ""
                print("Empty text {}".format(msg))

            thread["msg_counter"] = 1
            last_ts = datetime.datetime.fromtimestamp(msg['ts'])
            thread["start_ts"] = last_ts

            if "reactions_" in msg and msg["reactions_"]:
                thread["reactions_"] = msg["reactions_"]
                self.threads.append(copy.deepcopy(thread))

            processed_ids.append(i)
            for submsg_index in self.threads_index[self.key_str(key)]:
                submsg = self.messages[submsg_index]
                submsg_ts = datetime.datetime.fromtimestamp(submsg['ts'])
                if submsg_ts < last_ts:
                    raise Exception("""Wrong order in timestamps. submsg_ts {}\n\n
                                     last_msg {}\n\n submsg {}\n\n msg {}"""
                                    .format(submsg_ts, last_ts, submsg, msg))
                last_ts = submsg_ts
                thread["msg_counter"] += 1
                subtext = self.get_text(submsg)
                if subtext:
                    thread["text"] += " ".join([subtext, EOU_TOKEN])
                else:
                    print("Empty text {}".format(submsg))
                #TODO rip attachment
                if "reactions_" in submsg and submsg["reactions_"]:
                    thread["reactions_"] = submsg["reactions_"]
                    thread["end_ts"] = submsg_ts
                    self.threads.append(copy.deepcopy(thread))
                processed_ids.append(i)





def _extract_slack_link_id(m):
    return m.group('id')


def normalize_links(text):
    return re_slack_link.sub(_extract_slack_link_id, text)


if __name__ == '__main__':
    dir = '../input/export_Feb_8_2018'
    BASE_DIR = Path("/home/algis/repos/personal/MOOC/ODS_dump/input/export_Feb_8_2018")

    loader = SlackLoader2(dir, exclude_channels=[], only_channels=['_jobs'])
    print(len(loader.messages))
    print(len(loader.threads))
    type(loader.threads)
