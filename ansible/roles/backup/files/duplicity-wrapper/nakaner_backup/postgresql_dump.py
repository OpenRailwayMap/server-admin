import logging
import pwd
import os
import os.path
import tempfile
from .utils import run_cmd

class PostgreSqlDump:
    def __init__(self, source):
        self.source = source
        source_filename = os.path.basename(source)
        self.output = tempfile.mkstemp(suffix="{}.sql".format(source_filename), text=True)
        postgres_uid = pwd.getpwnam("postgres").pw_uid
        os.chown(self.output[1], postgres_uid, 0)

    def run(self):
        logging.info('Creating a backup of {} at {}'.format(self.source, self.output[1]))
        cmd_args = ["pg_dump", "--format", "plain", "--file", self.output[1], self.source]
        if run_cmd(cmd_args, user="postgres"):
            return True, self.output[1]
        os.remove(self.output[1])
        return False, None
