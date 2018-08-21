def setup_module(module):
    module.TestStateFullThing.classcount = 0

class TestStateFullThing:
    def setup_class(cls):
        cls.classcount += 1

    def teardown_class(cls):
        cls.classcount -= 1

    def setup_method(self, method):
        self.id = eval(method.func_name[5:])

    def test_42(self):
        assert self.classcount == 1
        assert self.id == 42

    def test_23(self):
        assert self.classcount == 1
        assert self.id == 23

def teardown_module(module):
    assert module.TestStateFullThing.classcount == 0
    