from async_response import AsyncResponse

class ResponseData(object):
    def __init__(self, do_after_done=None):
        self.parameter_dict = {}
        if do_after_done:
            self.do_after_done = do_after_done
        else:
            self.do_after_done = lambda x : x

    def add_response_data(self, key, resp):
        self.parameter_dict[key] = resp

    def _unpack_responses(self):
        for key in self.parameter_dict.keys():
            self.parameter_dict[key] = self.parameter_dict[key].get_response()

    def get_response(self):
        self._unpack_responses()
        return self.do_after_done(self.parameter_dict)

class ResponseCollector(object):

    def __init__(self):
        self.resp_dict = {}

    def add_response(self, key, parameter, resp, do_after_done=None):
        if not self.resp_dict.has_key(key):
            self.resp_dict[key] = ResponseData(do_after_done)

        self.resp_dict[key].add_response_data(parameter, resp)


    def is_done(self):
        is_done = True

        for responses in self.resp_dict.values():
            for resp in responses.parameter_dict.values():
                if type(resp) is AsyncResponse and not resp.is_done():
                    is_done = False

        return is_done

    def _unpack_responses(self):
        for key in self.resp_dict.keys():
            self.resp_dict[key] = self.resp_dict[key].get_response()


    def get_response(self):
        self._unpack_responses()
        return self.resp_dict


