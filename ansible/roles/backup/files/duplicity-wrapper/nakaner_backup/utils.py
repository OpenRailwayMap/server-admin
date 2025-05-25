import logging
import shlex
import subprocess


def log_process(pipe):
    for line in iter(pipe.readline, b''):
        logging.debug(line)

def run_cmd(cmd_args, retry_count=3, user=None):
    count = 0
    while count < retry_count:
        if count > 0:
            logging.warning('Failed to execute command, trying again (attempt {} of {}): {}'.format(shlex.join(cmd_args), count+1, retry_count))
        logging.debug('Running command: {}'.format(shlex.join(cmd_args)))
        process = subprocess.Popen(cmd_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, user=user)
        with process.stdout:
            log_process(process.stdout)
        returncode = process.wait()
        if returncode != 0:
            logging.warning('Got exitcode {} from: {}'.format(returncode, shlex.join(cmd_args)))
        return returncode == 0
    logging.error('Could not execute command, failed in all {} attempts: {}'.format(retry_count, shlex.join(cmd_args)))
    return False
