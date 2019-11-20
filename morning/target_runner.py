
from morning.logging import logger



class TargetRunner:
    def __init__(self, msg_queue, target, pipelines):
        self.msg_queue = msg_queue
        self.streams = []
        self.main_stream = None
        self.setup_stream(pipelines)
    
    def is_realtime(self):
        return self.main_stream == None

    def setup_stream(self, pipelines):
        for p in pipelines:
            self.streams.append(p['stream'])

        for stream in self.streams:
            if stream.have_clock():
                self.main_stream = stream

        if self.main_stream is not None:
            for stream in self.streams:
                if self.main_stream is not stream:
                    self.main_stream.add_child_streams(stream)

    def db_clock_start(self):
        pass