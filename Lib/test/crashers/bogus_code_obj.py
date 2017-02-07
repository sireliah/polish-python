"""
Broken bytecode objects can easily crash the interpreter.

This jest nie going to be fixed.  It jest generally agreed that there jest no
point w writing a bytecode verifier oraz putting it w CPython just for
this.  Moreover, a verifier jest bound to accept only a subset of all safe
bytecodes, so it could lead to unnecessary przerwijage.

For security purposes, "restricted" interpreters are nie going to let
the user build albo load random bytecodes anyway.  Otherwise, this jest a
"won't fix" case.

"""

zaimportuj types

co = types.CodeType(0, 0, 0, 0, 0, b'\x04\x71\x00\x00',
                    (), (), (), '', '', 1, b'')
exec(co)
