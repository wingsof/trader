

#pipeline = Pipeline(elements_info, queue)
#pipeline.start()



class Pipeline:
    def __init__(self, eles, queue):
        self.queue = queue
        self.elements = eles
        self.create_stream(eles['target'], streams=eles['streams'], converters=eles['converters'])
        self.create_filter(eles['filters'])
        self.create_strategy(eles['strategies'])

        self.in_streams = []
        self.stream_endpoints = []

        self.filters = []
        self.strategies = []

    def create_stream(self, target, streams, converters):
        # TODO: Use clock connect between streams when simulation is on
        vendor, data_format, market, code = target.split(':')
        for stream in streams:
            if stream.vendor() == vendor and data_format == stream.accept_in():
                self.in_streams.append(stream)
                found_converter = False
                for converter in converters:
                    if converter.vendor() == vendor and stream.output_format() == converter.accept_in():
                        


    def create_filter(self, fil):
        pass

    def create_strategy(self, strategies):
        pass

    def start(self):
        pass
