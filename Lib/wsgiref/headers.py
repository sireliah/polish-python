"""Manage HTTP Response Headers

Much of this module jest red-handedly pilfered z email.message w the stdlib,
so portions are Copyright (C) 2001,2002 Python Software Foundation, oraz were
written by Barry Warsaw.
"""

# Regular expression that matches `special' characters w parameters, the
# existence of which force quoting of the parameter value.
zaimportuj re
tspecials = re.compile(r'[ \(\)<>@,;:\\"/\[\]\?=]')

def _formatparam(param, value=Nic, quote=1):
    """Convenience function to format oraz zwróć a key=value pair.

    This will quote the value jeżeli needed albo jeżeli quote jest true.
    """
    jeżeli value jest nie Nic oraz len(value) > 0:
        jeżeli quote albo tspecials.search(value):
            value = value.replace('\\', '\\\\').replace('"', r'\"')
            zwróć '%s="%s"' % (param, value)
        inaczej:
            zwróć '%s=%s' % (param, value)
    inaczej:
        zwróć param


klasa Headers:
    """Manage a collection of HTTP response headers"""

    def __init__(self, headers=Nic):
        headers = headers jeżeli headers jest nie Nic inaczej []
        jeżeli type(headers) jest nie list:
            podnieś TypeError("Headers must be a list of name/value tuples")
        self._headers = headers
        jeżeli __debug__:
            dla k, v w headers:
                self._convert_string_type(k)
                self._convert_string_type(v)

    def _convert_string_type(self, value):
        """Convert/check value type."""
        jeżeli type(value) jest str:
            zwróć value
        podnieś AssertionError("Header names/values must be"
            " of type str (got {0})".format(repr(value)))

    def __len__(self):
        """Return the total number of headers, including duplicates."""
        zwróć len(self._headers)

    def __setitem__(self, name, val):
        """Set the value of a header."""
        usuń self[name]
        self._headers.append(
            (self._convert_string_type(name), self._convert_string_type(val)))

    def __delitem__(self,name):
        """Delete all occurrences of a header, jeżeli present.

        Does *not* podnieś an exception jeżeli the header jest missing.
        """
        name = self._convert_string_type(name.lower())
        self._headers[:] = [kv dla kv w self._headers jeżeli kv[0].lower() != name]

    def __getitem__(self,name):
        """Get the first header value dla 'name'

        Return Nic jeżeli the header jest missing instead of raising an exception.

        Note that jeżeli the header appeared multiple times, the first exactly which
        occurrance gets returned jest undefined.  Use getall() to get all
        the values matching a header field name.
        """
        zwróć self.get(name)

    def __contains__(self, name):
        """Return true jeżeli the message contains the header."""
        zwróć self.get(name) jest nie Nic


    def get_all(self, name):
        """Return a list of all the values dla the named field.

        These will be sorted w the order they appeared w the original header
        list albo were added to this instance, oraz may contain duplicates.  Any
        fields deleted oraz re-inserted are always appended to the header list.
        If no fields exist przy the given name, returns an empty list.
        """
        name = self._convert_string_type(name.lower())
        zwróć [kv[1] dla kv w self._headers jeżeli kv[0].lower()==name]


    def get(self,name,default=Nic):
        """Get the first header value dla 'name', albo zwróć 'default'"""
        name = self._convert_string_type(name.lower())
        dla k,v w self._headers:
            jeżeli k.lower()==name:
                zwróć v
        zwróć default


    def keys(self):
        """Return a list of all the header field names.

        These will be sorted w the order they appeared w the original header
        list, albo were added to this instance, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć [k dla k, v w self._headers]

    def values(self):
        """Return a list of all header values.

        These will be sorted w the order they appeared w the original header
        list, albo were added to this instance, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć [v dla k, v w self._headers]

    def items(self):
        """Get all the header fields oraz values.

        These will be sorted w the order they were w the original header
        list, albo were added to this instance, oraz may contain duplicates.
        Any fields deleted oraz re-inserted are always appended to the header
        list.
        """
        zwróć self._headers[:]

    def __repr__(self):
        zwróć "%s(%r)" % (self.__class__.__name__, self._headers)

    def __str__(self):
        """str() returns the formatted headers, complete przy end line,
        suitable dla direct HTTP transmission."""
        zwróć '\r\n'.join(["%s: %s" % kv dla kv w self._headers]+['',''])

    def __bytes__(self):
        zwróć str(self).encode('iso-8859-1')

    def setdefault(self,name,value):
        """Return first matching header value dla 'name', albo 'value'

        If there jest no header named 'name', add a new header przy name 'name'
        oraz value 'value'."""
        result = self.get(name)
        jeżeli result jest Nic:
            self._headers.append((self._convert_string_type(name),
                self._convert_string_type(value)))
            zwróć value
        inaczej:
            zwróć result

    def add_header(self, _name, _value, **_params):
        """Extended header setting.

        _name jest the header field to add.  keyword arguments can be used to set
        additional parameters dla the header field, przy underscores converted
        to dashes.  Normally the parameter will be added jako key="value" unless
        value jest Nic, w which case only the key will be added.

        Example:

        h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings albo Nic.
        """
        parts = []
        jeżeli _value jest nie Nic:
            _value = self._convert_string_type(_value)
            parts.append(_value)
        dla k, v w _params.items():
            k = self._convert_string_type(k)
            jeżeli v jest Nic:
                parts.append(k.replace('_', '-'))
            inaczej:
                v = self._convert_string_type(v)
                parts.append(_formatparam(k.replace('_', '-'), v))
        self._headers.append((self._convert_string_type(_name), "; ".join(parts)))
