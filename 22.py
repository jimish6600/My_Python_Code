class myclass:
    def __init__(self,value):
        self._value = value
    @property
    def ten_value(self):
        return 10* self._value
    @ten_value.setter
    def ten_value(self,n_value):
        self._value=n_value/10

class youclass(myclass):
    b="d"

o = myclass(10)

print(o.ten_value)

o.ten_value = 12

print(o._value)