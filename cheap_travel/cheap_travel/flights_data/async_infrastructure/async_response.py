from response_collector import ResponseCollector
import time


class AsyncResponse(object):

    def __init__(self, do_after_done=False):
        self.done = False
        self.do_after_done = do_after_done
        self.response_value = None

    def make_done(self):
        self.done = True

    def _calculate_if_done(self):
        pass

    def is_done(self):
        self._calculate_if_done()
        return self.done

    def wait_for_response(self):
        while not self.done:
            self._calculate_if_done()
            time.sleep(1)

    def _calculate_response(self):
        if self.do_after_done:
            return self.do_after_done(self.response_value)

    def get_response(self):
        self.wait_for_response()
        return self._calculate_response()

    def set_response_value(self, resp):
        self.done = True
        self.response_value = resp


def AsyncMultiResponse(AsyncResponse):
    def __init__(self, resp_collector, do_after_done=None):
        super(AsyncResponse, self).__init__(do_after_done)
        self.resp_collector = resp_collector

    def _calculate_if_done(self):
        if self.resp_collector.is_done():
            self.done = True

    def _calculate_response(self):
        resp = self.resp_collector.get_respnse()
        if self.do_after_done:
            resp = self.do_after_done(resp)

        return resp

