
# !/usr/bin/env python3
import os
import datetime
import logging
import signal
import argparse
import time




logger = logging.getLogger(__file__)
exit_flag = False
found_files = []
w_magic = {}

def create_parser():
    """Creates Parser and sets up command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--ext', type=str, default='.txt',
                         help='Text file extention to watch')
    parser.add_argument('-i', '--interval', type=float,
                         default=1, help='Number of seconds between polling')
    parser.add_argument('path', help='Directory path to watch')
    parser.add_argument('magic', help='String to watch for')
    return parser

def find_magic(filename, w_magic, directory):
    global word_magic
    with open(directory + '/' + filename) as f:
        for i, line in enumerate(f.readlines(), 1):
            if w_magic in line and i > word_magic[filename]:
                logger.info('Discovered magic word: {} on line: {}'
                            ' in file: {}'.format(w_magic, i, filename))
            if i  >  word_magic[filename]:
                word_magic[filename] += 1

def watch_directory(args):
    global found_files
    global word_magic
    
    logger.info('Watching directory: {}, File Ext: {}, Polling Interval: {}, '
                'Magic Text: {}'.format(args.path, args.ext, args.interval, args.magic
                ))
    directory = os.path.abspath(args.path)
    file_directory = os.listdir(directory)
    for file in file_directory:
        if file.endswith(args.ext) and file not in found_files:
            logger.info('New file: {} found in {}'.format(file, args.path))
            found_files.append(file)
            word_magic[file] = 0
    for file in found_files:
        if file not in file_directory:
            logger.info('File: {} removed from {}'
                              .format(file, args.path))
            found_files.remove(file)
        del word_magic[file]
    for file in found_files:
        find_magic(file, args.magic, directory)


def handle_signal(sig_num, frame):
    """
    This is a handler for SIGTERM and SIGINT. Other signals can be mapped here as well (SIGHUP?)
    Basically it just sets a global flag, and main() will exit it's loop if the signal is trapped.
    :param sig_num: The integer signal number that was trapped from the OS.
    :param frame: Not used
    :return None
    """
    global exit_flag
    signames = dict((k, v) for v, k in reversed(sorted(signal.__dict__.items()))
        if v.startswith('SIG') and not v.startswith('SIG_'))
    logger.warning('Received signal: '
                   + signames[sig_num])
    if sig_num == signal.SIGINT or signal.SIGTERM:
        exit_flag = True



def main():
    # Hook these two signals from the OS ..
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(name)-12s %(levelname)-8s'
        '[%(threadName)-12s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger.setLevel(logging.DEBUG)
    app_start_time = datetime.datetime.now()
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '    Running {0}\n'
        '    Started on {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, app_start_time.isoformat())
    )
    parser = create_parser()
    args = parser.parse_args()
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while not exit_flag:
        try:
            watch_directory(args)
        except OSError:
            logger.error('{} directory does not exist'.format(args.path))
            time.sleep(args.interval*2)
        except Exception as e:
            logger.error('Unhandled exception: {}'.format(e))
            time.sleep(args.interval)

    uptime = datetime.datetime.now()-app_start_time
    logger.info(
        '\n'
        '-------------------------------------------------------------------\n'
        '    Stopped {0}\n'
        '    Uptime was {1}\n'
        '-------------------------------------------------------------------\n'
        .format(__file__, str(uptime))
    )


if __name__ == '__main__':
    main()
