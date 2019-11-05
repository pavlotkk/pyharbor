import signal


class GracefulInterruptHandler(object):
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig
        self.released = False

    def __enter__(self):

        self.interrupted = False
        self.released = False

        self.original_handler = signal.getsignal(self.sig)

        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)

        return self

    def __exit__(self, type, value, tb):
        self.release()

    def release(self):

        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)

        self.released = True

        return True


def trim_content(text: str) -> str:
    if not text:
        return ''

    max_words = 30
    words = text.split(maxsplit=max_words + 1)
    total_words = len(words)
    if total_words < max_words:
        max_words = total_words
    return ' '.join(words[:max_words - 1]) + '...'
