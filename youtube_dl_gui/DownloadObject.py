#!/usr/bin/env python2

''' Python module to download videos using youtube-dl & subprocess. '''

import os
import sys
import locale
import subprocess


class DownloadObject(object):

    '''
    Download videos using youtube-dl & subprocess.

    Params
        youtubedl_path: Absolute path of youtube-dl.
        data_hook: Can be any function with one parameter, the data.
        logger: Can be any logger which implements log().

    Accessible Methods
        download()
            Params: URL to download
                    Options list e.g. ['--help']

            Return: DownlaodObject.OK
                    DownloadObject.ERROR
                    DownloadObject.STOPPED
                    DownloadObject.ALREADY
        stop()
            Params: None

            Return: None

        clear_dash()
            Params: None

            Return: None

    Properties
        files_list: Python list that contains all the files DownloadObject
                    instance has downloaded.

    Data_hook Keys
        'playlist_index',
        'playlist_size',
        'filesize',
        'filename',
        'percent',
        'status',
        'speed',
        'eta'
    '''

    # download() return codes
    OK = 0
    ERROR = 1
    STOPPED = 2
    ALREADY = 3

    def __init__(self, youtubedl_path, data_hook=None, logger=None):
        self.youtubedl_path = youtubedl_path
        self.data_hook = data_hook
        self.logger = logger

        self._return_code = 0
        self._files_list = []
        self._proc = None

        self._data = {
            'playlist_index': None,
            'playlist_size': None,
            'filesize': None,
            'filename': None,
            'percent': None,
            'status': None,
            'speed': None,
            'eta': None
        }

    @property
    def files_list(self):
        ''' Return list that contains all files
        DownloadObject has downloaded.
        '''
        return self._files_list

    def download(self, url, options):
        ''' Download given url using youtube-dl &
        return self._return_code.
        '''
        self._return_code = self.OK

        cmd = self._get_cmd(url, options)
        self._create_process(cmd)

        while self._proc_is_alive():
            stdout, stderr = self._read()

            data = extract_data(stdout)

            if self._update_data(data):
                self._hook_data()

            if stderr != '':
                self._return_code = self.ERROR
                self._log(stderr)

        return self._return_code

    def stop(self):
        ''' Stop downloading. '''
        if self._proc_is_alive():
            self._proc.kill()
            self._return_code = self.STOPPED

    def clear_dash(self):
        ''' Clear DASH files after ffmpeg mux. '''
        for dash_file in self._files_list:
            if os.path.exists(dash_file):
                os.remove(dash_file)

    def _update_data(self, data):
        ''' Update self._data from data.
        Return True if updated else return False.
        '''
        updated = False

        for key in data:
            if key == 'filename':
                # Save full file path on self._files_list
                self._add_on_files_list(data['filename'])
                # Keep only the filename on data['filename']
                data['filename'] = os.path.basename(data['filename'])

            if key == 'status':
                # Set self._return_code to already downloaded
                if data[key] == 'Already Downloaded':
                    self._return_code = self.ALREADY
                    # Trash that key
                    data[key] = None

            self._data[key] = data[key]

            if not updated:
                updated = True

        return updated

    def _add_on_files_list(self, filename):
        ''' Add filename on self._files_list. '''
        self._files_list.append(filename)

    def _log(self, data):
        ''' Log data using self.logger. '''
        if self.logger is not None:
            self.logger.log(data)

    def _hook_data(self):
        ''' Pass self._data back to data_hook. '''
        if self.data_hook is not None:
            self.data_hook(self._data)

    def _proc_is_alive(self):
        ''' Return True if self._proc is alive. '''
        if self._proc is None:
            return False

        return self._proc.poll() is None

    def _read(self):
        ''' Read subprocess stdout, stderr. '''
        stdout = stderr = ''

        stdout = self._read_stream(self._proc.stdout)

        if stdout == '':
            stderr = self._read_stream(self._proc.stderr)

        return stdout, stderr

    def _read_stream(self, stream):
        ''' Read subprocess stream. '''
        if self._proc is None:
            return ''

        data = stream.readline()
        return data.rstrip()

    def _get_cmd(self, url, options):
        ''' Return command for subprocess. '''
        if os.name == 'nt':
            cmd = [self.youtubedl_path] + options + [url]
        else:
            cmd = ['python', self.youtubedl_path] + options + [url]

        return cmd

    def _create_process(self, cmd):
        ''' Create new subprocess. '''
        encoding = info = None

        # Hide subprocess window on Windows
        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        # Encode command for subprocess
        # Refer to http://stackoverflow.com/a/9951851/35070
        if sys.version_info < (3, 0) and sys.platform == 'win32':
            try:
                encoding = locale.getpreferredencoding()
                u'TEST'.encode(encoding)
            except:
                encoding = 'UTF-8'

        if encoding is not None:
            cmd = [item.encode(encoding, 'ignore') for item in cmd]

        self._proc = subprocess.Popen(cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      startupinfo=info)


def extract_data(stdout):
    ''' Extract data from youtube-dl stdout. '''
    data_dictionary = {}

    stdout = [string for string in stdout.split(' ') if string != '']

    if len(stdout) == 0:
        return data_dictionary

    header = stdout.pop(0)

    if header == '[download]':
        data_dictionary['status'] = 'Downloading'

        # Get filename
        if stdout[0] == 'Destination:':
            data_dictionary['filename'] = ' '.join(stdout[1:])

        # Get progress info
        if '%' in stdout[0]:
            if stdout[0] == '100%':
                data_dictionary['speed'] = ''
                data_dictionary['eta'] = ''
            else:
                data_dictionary['percent'] = stdout[0]
                data_dictionary['filesize'] = stdout[2]
                data_dictionary['speed'] = stdout[4]
                data_dictionary['eta'] = stdout[6]

        # Get playlist info
        if stdout[0] == 'Downloading' and stdout[1] == 'video':
            data_dictionary['playlist_index'] = stdout[2]
            data_dictionary['playlist_size'] = stdout[4]

        # Get file already downloaded status
        if stdout[-1] == 'downloaded':
            data_dictionary['status'] = 'Already Downloaded'

    elif header == '[ffmpeg]':
        data_dictionary['status'] = 'Post Processing'

    else:
        data_dictionary['status'] = 'Pre Processing'

    return data_dictionary
