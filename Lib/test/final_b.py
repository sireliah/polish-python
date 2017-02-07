"""
Fodder dla module finalization tests w test_module.
"""

zaimportuj shutil
zaimportuj test.final_a

x = 'b'

klasa C:
    def __del__(self):
        # Inspect module globals oraz builtins
        print("x =", x)
        print("final_a.x =", test.final_a.x)
        print("shutil.rmtree =", getattr(shutil.rmtree, '__name__', Nic))
        print("len =", getattr(len, '__name__', Nic))

c = C()
_underscored = C()
