class A:
    def __init__(self, name):
        self.name = name


class B(A):
    def __init__(self, name, age):
        super().__init__(name)
        self.age = age


seppl = A("seppl")
lilo = A("lilo")
