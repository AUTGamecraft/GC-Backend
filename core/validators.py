import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    if value:
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.pdf',
                            '.doc',
                            '.docx',
                            '.zip',
                            '.webm',
                            '.mkv',
                            '.flv',
                            '.vob',
                            '.ogv',
                            '.ogg',
                            '.rrc',
                            '.gifv',
                            '.mng',
                            '.mov',
                            '.avi',
                            '.qt',
                            '.wmv',
                            '.yuv',
                            '.rm',
                            '.asf',
                            '.amv',
                            '.mp4',
                            '.m4p',
                            '.m4v',
                            '.mpg',
                            '.mp2',
                            '.mpeg',
                            '.mpe',
                            '.mpv',
                            '.m4v',
                            '.svi',
                            '.3gp',
                            '.3g2',
                            '.mxf',
                            '.roq',
                            '.nsv',
                            '.flv',
                            '.f4v',
                            '.f4p',
                            '.f4a',
                            '.f4b'
                            ]
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')
