process = psutil.Process()

global updaterExitFlag
threadsExitFlag = [False]


def plurial(i):
    if i > 1:
        return 's'
    else:
        return ''
