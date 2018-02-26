import pandas as pd
from pathlib import Path
from odsemoji.slack_data_loader2 import  SlackLoader2, normalize_links


if __name__ == '__main__':
    BASE_DIR = Path("../input/export_Feb_8_2018")
    file_cache = Path("../input/all_threads.pkl.compress")

    channels = ['_jobs', 'career']

    if not file_cache.exists():
        loader = SlackLoader2(BASE_DIR, exclude_channels=[])#, only_channels=channels)
        print("Loaded messages {}".format(len(loader.messages)))
        loader.process_threads()
        print("Loaded threads {}".format(len(loader.threads)))
        df = pd.DataFrame(loader.threads).set_index(["channel_name", "start_ts"])
        df.to_pickle(str(file_cache), compression="gzip")
        print("Saved into {}".format(file_cache))

