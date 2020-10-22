

class ZmqProxyThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.proxy = None

    def last_received_message(self):
        if self.proxy:
            return self.proxy.last_received_message
        return None

    def run(self):
        if self.proxy:
            self.proxy.run()

    def stop(self):
        if self.proxy:
            self.proxy.stop()
