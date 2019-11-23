from morning.logging import logger


class TargetRunner:
    def __init__(self, msg_queue, target, pipelines):
        self.msg_queue = msg_queue
        self.target = target
        self.streams = []
        self.main_stream = None
        self.setup_stream(pipelines)
        self.setup_pipeline(pipelines)
    
    def setup_pipeline(self, pipelines):
        decision = None
        for p in pipelines:
            # filter and strategy is list type
            stream, converter, filt, strategy = p['stream'], p['converter'], p['filter'], p['strategy']
            if decision is None:
                decision = p['decision']
                decision.set_environ(self.target, self.msg_queue)

            stream.set_output(converter)
            prev_filt = converter # for when no filter
            if len(filt) > 0:
                converter.set_output(filt[0])
                prev_filt = filt[0]
                for f in filt[1:]:
                    prev_filt.set_output(f)
                    prev_filt = f
            for s in strategy:
                prev_filt.set_output(s)
                s.set_output(decision)

    def is_realtime(self):
        return self.main_stream == None

    def setup_stream(self, pipelines):
        for p in pipelines:
            self.streams.append(p['stream'])

        for stream in self.streams:
            stream.set_target(self.target)
            if stream.have_clock():
                self.main_stream = stream

        logger.print('stream set_target done')
        if self.main_stream is not None:
            for stream in self.streams:
                if self.main_stream is not stream:
                    self.main_stream.add_child_streams(stream)

    def db_clock_start(self):
        if self.main_stream:
            while self.main_stream.received([]) > 0:
                pass
