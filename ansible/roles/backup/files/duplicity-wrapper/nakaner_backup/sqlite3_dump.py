import logging
import os.path
import sqlite3
import tempfile

class Sqlite3Dump:
    def __init__(self, source):
        self.source = source
        source_filename = os.path.basename(source)
        self.output = tempfile.mkstemp(suffix="{}.sqlite3".format(source_filename), text=True)

    def run(self):
        logging.info('Creating a backup of {} at {}'.format(self.source, self.output))
        if not os.path.isfile(self.source) or os.path.islink(self.source):
            logging.error('Cannot open SQLite database {} because it is neither a file nor a symbolic link.'.format(self.source))
            return False, None
        try:
            with sqlite3.connect('file:{}?mode=ro'.format(self.source), uri=True) as src:
                with sqlite3.connect(self.output[1]) as dest:
                    src.backup(dest)
                dest.close()
            src.close()
        finally:
            return True, self.output[1]
