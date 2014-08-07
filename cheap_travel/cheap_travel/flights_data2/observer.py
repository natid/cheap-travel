
class Observer(object):
    def update(self, observable, *args, **kwargs):
        '''Called when the observed object is
        modified. You call an Observable object's
        notifyObservers method to notify all the
        object's observers of the change.'''
        pass


class Observable(object):
    def __init__(self):
        self.observers_list = []

    def add_observer(self, observer):
        if observer not in self.observers_list:
            self.observers_list.append(observer)

    def remove_observer(self, observer):
        self.observers_list.remove(observer)

    def notify_observers(self, *args, **kwargs):
        for observer in self.observers_list:
            observer.update(self, *args, **kwargs)
