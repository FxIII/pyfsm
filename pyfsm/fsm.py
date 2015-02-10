from pyee import EventEmitter
EventEmitter.off = EventEmitter.remove_listener
import re
class FSM:
    nameRe = re.compile("([^\/]+)\/?([^\[:]+)?(?:\[([^\]]+)\])?:?(.+)?")
    @classmethod
    def parseName(cls,name):
        matchs = cls.nameRe.match(name).groups()
        return dict(zip("event pre guard post".split(),matchs))
    def _makeEventHandler(self,event):
        def doEvent(*a,**k):
                k.update(_event=event)
                self.update(*a,**k)
        return doEvent
    def __init__(self,descr):
        self.descr = descr
        self. transitions = {}
        self.ev = EventEmitter()
        self.ctx = lambda:None
        self.current = descr.get("initial",None)
        for transition in descr.get("events",[]):
            transition.setdefault("from","None")
            parsed = self.parseName(transition["name"])
            self.transitions[transition["from"]+"-"+parsed["event"]] = transition
            eventHandler = self._makeEventHandler(parsed["event"])
            setattr(self.ev,parsed["event"],eventHandler)
        self.descr.setdefault("handlers",{})
    def update(self,*a,**k):
        event = k["_event"]
        del(k["_event"])
        try:
            transition = self.transitions[str(self.current)+"-"+event]
        except KeyError:
            return False
        self.trans = transition
        NOP = lambda*a,**k:None;
        TRUE = lambda*a,**k:True;
        parsed = self.parseName(transition["name"])
        pre = self.descr["handlers"].get(parsed["pre"],NOP)
        guard = self.descr["handlers"].get(parsed["guard"],TRUE)
        post = self.descr["handlers"].get(parsed["post"],NOP)

        pre(self,*a,**k)
        if (guard(self,*a,**k)):
            self.current = transition["to"]
            post(self,*a,**k)
            self.descr["handlers"].get(self.current,NOP)(self)
