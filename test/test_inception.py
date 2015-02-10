import unittest,pytest
from mock import patch,Mock


from pyfsm import FSM
class TestSignals(unittest.TestCase):
    def setUp(self):
        pass
    def test_nameParsing(self):
        "it should reconogize names format"
        names = [
            ("ev","ev",None,None,None),
            ("ev/pre","ev","pre",None,None),
            ("ev/:post","ev",None,None,"post"),
            ("ev/[guard]","ev",None,"guard",None),
            ("ev/pre:post","ev","pre",None,"post"),
            ("ev/pre[guard]","ev","pre","guard",None),
            ("ev/[guard]post","ev",None,"guard","post"),
            ("ev/pre[guard]post","ev","pre","guard","post"),
        ]
        for n,a,b,c,d in names:
            assert(FSM.nameRe.match(n).groups() == (a,b,c,d))
    def test_loadEvent(self):
        "it should load functions in ev"
        descr ={
            "events":[{"name":"step","from":"current","to":"next"}]
        }
        a = FSM(descr)
        assert hasattr(a.ev,"step")

    def test_loadInitial(self):
        "it should load initial state"
        descr={"initial":"defined"}
        a = FSM(descr)
        assert a.current == "defined"

    def test_implicitState(self):
        "it should allow implicit source state transition"
        descr={"events":[{"name":"step","to":"transitioned"}]}
        a = FSM(descr)
        a.ev.step()
        assert a.current== "transitioned"

    def test_preExecution(self):
        "it should execute pre"
        def pre(self):
            self.ctx.done=True
            assert(self.current != "transitioned")
        descr={
        "events":[{"name":"step/mypre","to":"transitioned"}],
        "handlers":{"mypre":pre}
        }
        a = FSM(descr)
        a.ctx.done=False
        a.ev.step()
        assert a.ctx.done

    def test_guardExecution(self):
        "it should execute guard"
        def guard(self):
            self.ctx.done=True
            return True
        descr={
        "events":[{"name":"step/[guard]","to":"transitioned"}],
        "handlers":{"guard":guard}
        }
        a = FSM(descr)
        a.ctx.done=False
        a.ev.step()
        assert a.ctx.done
        assert a.current == "transitioned"
    def test_postExecution(self):
        "it should execute post"
        def post(self):
            self.ctx.done=True
            assert(self.current == "transitioned")
        descr={
        "events":[{"name":"step/:post","to":"transitioned"}],
        "handlers":{"post":post}
        }
        a = FSM(descr)
        a.ctx.done=False
        a.ev.step()
        assert a.ctx.done

    def test_guardBlockExecution(self):
        "it should execute guard wihtout transitioning nor executing post"
        def guard(self):
            self.ctx.done=True
            return False
        def post(self):
            assert False
        def pre(self):
            self.ctx.preDone = True
        descr={
        "events":[{"name":"step/pre[guard]post","to":"transitioned"}],
        "handlers":{"guard":guard,"post":post,"pre":pre}
        }
        a = FSM(descr)
        a.ctx.preDone=False
        a.ctx.done=False
        a.ev.step()
        assert a.ctx.done
        assert a.ctx.preDone
        assert a.current != "transitioned"
    def test_guardFullExecution(self):
        "it should execute guard than transitioning then executing post"
        def guard(self):
            self.ctx.done = True
            return True
        def post(self):
            self.ctx.postDone = True
        def pre(self):
            self.ctx.preDone = True
        descr={
        "events":[{"name":"step/pre[guard]post","to":"transitioned"}],
        "handlers":{"guard":guard,"post":post,"pre":pre}
        }
        a = FSM(descr)
        a.ctx.preDone=False
        a.ctx.done=False
        a.ctx.postDone=False
        a.ev.step()
        assert a.ctx.preDone
        assert a.ctx.done
        assert a.ctx.postDone
        assert a.current == "transitioned"

