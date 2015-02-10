import unittest,pytest
from mock import patch,Mock,call


from pyfsm import yamlFSM
class TestYamlFSM(unittest.TestCase):
    def setUp(self):
        pass
    def test_test(self):
        "it should count"
        class Counter(yamlFSM):
            """
            initial: resetted
            events:
                - name: reset/init
                  from: resetted
                  to: counting
                - name: count/incr[limitReached]overflow
                  from: counting
                  to: terminated
                - name: quit
                  from: counting
                  to: terminated
            """
            def init(self,initial=0,max=None):
                self.ctx.val = initial
                self.ctx.max = max
            def incr(self,delta=1):
                self.ctx.val += delta
                self.ev.emit("count",self.ctx.val)
            def limitReached(self,*a):
                if self.ctx.max is None:
                    return False
                return self.ctx.max == self.ctx.val
            def overflow(self,*a):
                self.ev.emit("overflow",self.ctx.val)
            def terminated(self):
                self.ev.emit("enough",self.ctx.val)
        onOverflow = Mock()
        onEnough = Mock()
        showMe = Mock()

        counter = Counter()
        counter.ev.reset(0,12)
        counter.ev.on("overflow",onOverflow)
        counter.ev.on("enough",onEnough)
        counter.ev.on("count",showMe)

        counter.ev.count()
        counter.ev.count(10)
        counter.ev.quit()
        counter.ev.count()
        counter.ev.count()
        assert not onOverflow.called
        assert onEnough.called
        assert showMe.call_args_list == [call(1),call(11)]
