#! /usr/bin/env python3

import argparse
import json
import logging
import os
import sys

from nakaner_backup.postgresql_dump import PostgreSqlDump
from nakaner_backup.utils import run_cmd

def get_ssh_options(ssh_key):
    return ['--ssh-options="-oPasswordAuthentication=no -oIdentityFile={}"'.format(ssh_key)]

def get_gpg_options(gpg_key_id):
    if gpg_key_id is not None:
        return ["--encrypt-key", gpg_key_id]
    return ["--no-encryption"]

def duplicity(source, target_host, target_directory, ssh_key, gpg_key_id, preparation=None):
    command_line_args = ["duplicity", "incremental", "--full-if-older-than", "2W"] + get_gpg_options(gpg_key_id) + get_ssh_options(ssh_key)
    if preparation:
        command_line_args += ["--allow-source-mismatch"]
    command_line_args += [source, "sftp://{}/{}".format(target_host, target_directory)]
    return run_cmd(command_line_args)


def drop_old_backups(target_host, target_directory, ssh_key, gpg_key_id):
    logging.info('Checking for old full backups to delete.')
    command_line_args = ["duplicity", "remove-all-but-n-full", "3"] + get_gpg_options(gpg_key_id) + get_ssh_options(ssh_key)
    if preparation:
        command_line_args += ["--allow-source-mismatch"]
    command_line_args += ["ssh://{}/{}".format(target_host, target_directory)]
    return run_cmd(command_line_args)


def run_task(task, log_level, host, ssh_key, gpg_key_id):
    success = False
    logging.info("Running task {}".format(task['name']))
    pre_run = task.get('pre_run', '')
    source = task.get('source')
    ssh_compression = task.get('ssh_compression', False)
    if type(ssh_compression) is not bool:
        logging.critical('Task {}: Option ssh_compression must have boolean type.'.format(task['name']))
        return False
    if source is None:
        logging.critical('Task {}: Source is not set.'.format(task['name']))
        return False
    target_directory = task.get('target_directory', '')
    preparation = None
    preparation_output_path = None
    try:
        if pre_run == 'sqlite3_dump':
            preparation = Sqlite3Dump(source)
        elif pre_run == 'postgresql_dump':
            preparation = PostgreSqlDump(source)
        if preparation is not None:
            preparation_result, preparation_output_path = preparation.run()
            if not preparation_result:
                logging.fatal("Preparation of task {} failed.".format(task["name"]))
                return False
            source = preparation_output_path
        if not duplicity(source=source, target_host=host, target_directory=target_directory, ssh_key=ssh_key, gpg_key_id=gpg_key_id, preparation=preparation):
            logging.error('Task {} failed (see above).'.format(task['name']))
        else:
            success = True
        if preparation_output_path:
            logging.debug('Deleting {}'.format(preparation_output_path))
            os.remove(preparation_output_path)
    except Exception as err:
        logging.exception(err)
        return False
    return success


def create_task(key, value):
    result = {k: v for k, v in value.items()}
    result["name"] = key
    return result


def main():
    parser = argparse.ArgumentParser(description='Run multiple duplicity tasks with pre-requirements (like database dumping)')
    parser.add_argument("-H", "--host", type=str, required=True, help="Target host ULR, e.g. ssh://user@hostname:port//absolute/path")
    parser.add_argument("-g", "--gpg-key", type=str, help="ID of GnuPG public key for encryption. Use --no-encryption if you intentionally do not specify as GPG key.")
    parser.add_argument("-k", "--ssh-key", type=str, required=True, help="Path to SSH private key")
    parser.add_argument("-l", "--log-level", help="log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)", default="INFO", type=str)
    parser.add_argument("--no-encryption", action="store_true", help="Do not encrypt backups.")
    parser.add_argument("-o", "--only-tasks", type=str, help="Only run specified tasks. Provide them as a list of names separated by comma.")
    parser.add_argument('tasks_file', type=argparse.FileType('r'), help='Tasks JSON file')
    args = parser.parse_args()

    # log level
    numeric_log_level = getattr(logging, args.log_level.upper())
    if not isinstance(numeric_log_level, int):
        raise ValueError("Invalid log level {}".format(args.log_level.upper()))
    logging.basicConfig(level=numeric_log_level)

    if not args.gpg_key and not args.no_encryption:
        logging.error('Missing GPG key but encryption requested.')
        sys.exit(1)

    config = json.load(args.tasks_file)
    only_tasks = []
    if args.only_tasks:
        only_tasks = args.only_tasks.split(",")
    failures = 0
    tasks = [create_task(k, v) for k, v in config.items()]
    if len(tasks) == 0:
        logging.error('No tasks provided.')
        sys.exit(1)
    for t in tasks:
        task_name = t.get('name', '')
        if task_name is None:
            logging.critical('Task name is missing')
            sys.exit(1)
        if len(only_tasks) > 0 and task_name not in only_tasks:
            logging.info('Skipping task {}'.format(task_name))
            continue
        r = run_task(t, args.log_level, args.host, ssh_key=args.ssh_key, gpg_key_id=args.gpg_key)
        if not r:
            logging.error('task {} failed'.format(task_name))
            failures += 1
    if failures > 0:
        logging.error('Backup completed for {} tasks successfully but {} tasks failed'.format(len(tasks) - failures, failures))
        sys.exit(1)
    else:
        logging.info('Backup completed successfully.')


if __name__ == '__main__':
    main()
