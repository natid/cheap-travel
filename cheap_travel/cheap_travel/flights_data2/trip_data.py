

class TripData(object):

    def __init__(self, origin, dest, depart_dates, return_dates=None):
        self.origin = origin
        self.dest = dest
        self.depart_dates = depart_dates
        if return_dates:
            self.return_dates = return_dates
        else:
            self.return_dates = []

    def compute_key(self):
        words_to_join = [self.origin, self.dest]

        for date in self.depart_dates:
            words_to_join.append(date)

        for date in self.return_dates:
            words_to_join.append(date)

        return "-".join(words_to_join)
