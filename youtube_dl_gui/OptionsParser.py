#!/usr/bin/env python2

''' Parse OptionsManager.options. '''

from .utils import (
    fix_path,
    is_dash
)

SUBS_LANG = {
    "English": "en",
    "Greek": "gr",
    "Portuguese": "pt",
    "French": "fr",
    "Italian": "it",
    "Russian": "ru",
    "Spanish": "es",
    "German": "de"
}

VIDEO_FORMATS = {
    "default": "0",
    "mp4 [1280x720]": "22",
    "mp4 [640x360]": "18",
    "webm [640x360]": "43",
    "flv [400x240]": "5",
    "3gp [320x240]": "36",
    "mp4 1080p(DASH)": "137",
    "mp4 720p(DASH)": "136",
    "mp4 480p(DASH)": "135",
    "mp4 360p(DASH)": "134"
}

DASH_AUDIO_FORMATS = {
    "none": "none",
    "DASH m4a audio 128k": "140",
    "DASH webm audio 48k": "171"
}

AUDIO_QUALITY = {
    "high": "0",
    "mid": "5",
    "low": "9"
}


class OptionsParser():

    '''
    Parse OptionsManager.options into youtube-dl options list.

    Params
        opt_manager: OptionsManager.OptionsManager object

    Accessible Methods
        parse()
            Params: None

            Return: Options list
    '''

    def __init__(self, opt_manager):
        self._options = opt_manager.options
        self.options_list = []

    def parse(self):
        ''' Parse OptionsHandler.options and return options list. '''
        self._set_progress_options()
        self._set_output_options()
        self._set_auth_options()
        self._set_connection_options()
        self._set_video_options()
        self._set_playlist_options()
        self._set_filesystem_options()
        self._set_subtitles_options()
        self._set_audio_options()
        self._set_other_options()
        return self.options_list

    def _set_progress_options(self):
        ''' Do NOT change this option. '''
        self.options_list.append('--newline')

    def _set_playlist_options(self):
        if self._options['playlist_start'] != 1:
            self.options_list.append('--playlist-start')
            self.options_list.append(str(self._options['playlist_start']))
        if self._options['playlist_end'] != 0:
            self.options_list.append('--playlist-end')
            self.options_list.append(str(self._options['playlist_end']))
        if self._options['max_downloads'] != 0:
            self.options_list.append('--max-downloads')
            self.options_list.append(str(self._options['max_downloads']))

    def _set_auth_options(self):
        if self._options['username'] != '':
            self.options_list.append('-u')
            self.options_list.append(self._options['username'])
        if self._options['password'] != '':
            self.options_list.append('-p')
            self.options_list.append(self._options['password'])
        if self._options['video_password'] != '':
            self.options_list.append('--video-password')
            self.options_list.append(self._options['video_password'])

    def _set_connection_options(self):
        if self._options['retries'] != 10:
            self.options_list.append('-R')
            self.options_list.append(str(self._options['retries']))
        if self._options['proxy'] != '':
            self.options_list.append('--proxy')
            self.options_list.append(self._options['proxy'])
        if self._options['user_agent'] != '':
            self.options_list.append('--user-agent')
            self.options_list.append(self._options['user_agent'])
        if self._options['referer'] != '':
            self.options_list.append('--referer')
            self.options_list.append(self._options['referer'])

    def _set_video_options(self):
        if self._options['video_format'] != 'default':
            self.options_list.append('-f')

            video_format = VIDEO_FORMATS[self._options['video_format']]

            if is_dash(self._options['video_format']):
                if is_dash(self._options['dash_audio_format']):
                    dash_format = DASH_AUDIO_FORMATS[self._options['dash_audio_format']]

                    video_format += '+' + dash_format

            self.options_list.append(video_format)

    def _set_filesystem_options(self):
        if self._options['ignore_errors']:
            self.options_list.append('-i')
        if self._options['write_description']:
            self.options_list.append('--write-description')
        if self._options['write_info']:
            self.options_list.append('--write-info-json')
        if self._options['write_thumbnail']:
            self.options_list.append('--write-thumbnail')
        if self._options['min_filesize'] != '0':
            self.options_list.append('--min-filesize')
            self.options_list.append(self._options['min_filesize'])
        if self._options['max_filesize'] != '0':
            self.options_list.append('--max-filesize')
            self.options_list.append(self._options['max_filesize'])

    def _set_subtitles_options(self):
        if self._options['write_all_subs']:
            self.options_list.append('--all-subs')
        if self._options['write_auto_subs']:
            self.options_list.append('--write-auto-sub')
        if self._options['write_subs']:
            self.options_list.append('--write-sub')
            self.options_list.append('--sub-lang')
            self.options_list.append(SUBS_LANG[self._options['subs_lang']])
        if self._options['embed_subs']:
            self.options_list.append('--embed-subs')

    def _set_output_options(self):
        save_path = fix_path(self._options['save_path'])
        self.options_list.append('-o')

        if self._options['output_format'] == 'id':
            self.options_list.append(save_path + '%(id)s.%(ext)s')
        elif self._options['output_format'] == 'title':
            self.options_list.append(save_path + '%(title)s.%(ext)s')
        elif self._options['output_format'] == 'custom':
            self.options_list.append(save_path + self._options['output_template'])

        if self._options['restrict_filenames']:
            self.options_list.append('--restrict-filenames')

    def _set_audio_options(self):
        if self._options['to_audio']:
            self.options_list.append('-x')
            self.options_list.append('--audio-format')
            self.options_list.append(self._options['audio_format'])
            if self._options['audio_quality'] != 'mid':
                self.options_list.append('--audio-quality')
                self.options_list.append(AUDIO_QUALITY[self._options['audio_quality']])
            if self._options['keep_video']:
                self.options_list.append('-k')

    def _set_other_options(self):
        if self._options['cmd_args'] != '':
            for option in self._options['cmd_args'].split():
                self.options_list.append(option)
