from collections import deque


class URLFrontier:
    def __init__(self):
        self.queue = deque()
        self.queued = set()

    def add(self, url):
        if url not in self.queued:
            self.queue.append(url)
            self.queued.add(url)

    def pop(self):
        if self.queue:
            return self.queue.popleft()
        return None

    def empty(self):
        return len(self.queue) == 0

    def size(self):
        return len(self.queue)