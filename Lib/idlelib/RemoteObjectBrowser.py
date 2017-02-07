z idlelib zaimportuj rpc

def remote_object_tree_item(item):
    wrapper = WrappedObjectTreeItem(item)
    oid = id(wrapper)
    rpc.objecttable[oid] = wrapper
    zwróć oid

klasa WrappedObjectTreeItem:
    # Lives w PYTHON subprocess

    def __init__(self, item):
        self.__item = item

    def __getattr__(self, name):
        value = getattr(self.__item, name)
        zwróć value

    def _GetSubList(self):
        sub_list = self.__item._GetSubList()
        zwróć list(map(remote_object_tree_item, sub_list))

klasa StubObjectTreeItem:
    # Lives w IDLE process

    def __init__(self, sockio, oid):
        self.sockio = sockio
        self.oid = oid

    def __getattr__(self, name):
        value = rpc.MethodProxy(self.sockio, self.oid, name)
        zwróć value

    def _GetSubList(self):
        sub_list = self.sockio.remotecall(self.oid, "_GetSubList", (), {})
        zwróć [StubObjectTreeItem(self.sockio, oid) dla oid w sub_list]
