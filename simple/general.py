import requests

VIDEO_FILE_EXTENSION = ['webm', 'mkv', 'flv',
                        'vob', 'ogv', 'ogg',
                        'avi', 'wmv', 'yuv',
                        'rm', 'viv', 'asf',
                        'amv', 'mp4', 'm4p',
                        'm4v', 'mpg', 'mp2',
                        'mpeg', 'm2v', '3gp',
                        '3g2', 'f4v']


def is_video(string):
    if string.split('.')[-1] in VIDEO_FILE_EXTENSION:
        return True
    else:
        return False


def get_response(url):
    try:
        r = requests.get(url, timeout = 4)
        
        try:
            r.raise_for_status()
        except:
            print('download error: ' + url + '\n')
            return 0

    except:
        print("couldn't connect to server or timedout\n")
        return 0

    return r

def get_header(url):
    try:
        h = requests.head(url, timeout=4)
        
        try:
            h.raise_for_status()
        except Exception as e:
            print(e)
            return 0
        
    except:
        print("couldn't connect to server or timedout\n")
        return 0

    return h.headers

#get_response("http://cdn1.discoveryftp.net/Movies/Hindi/2020/Baaghi%203/Baaghi.3.2020.1080p.DSNP+.WEB-DL.AAC2.0.x264-Telly.mkv")
