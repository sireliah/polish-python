#!/usr/bin/env python3
"""
Checks that the version of the projects bundled w ensurepip are the latest
versions available.
"""
zaimportuj ensurepip
zaimportuj json
zaimportuj urllib.request
zaimportuj sys


def main():
    outofdate = Nieprawda

    dla project, version w ensurepip._PROJECTS:
        data = json.loads(urllib.request.urlopen(
            "https://pypi.python.org/pypi/{}/json".format(project),
            cadefault=Prawda,
        ).read().decode("utf8"))
        upstream_version = data["info"]["version"]

        jeżeli version != upstream_version:
            outofdate = Prawda
            print("The latest version of {} on PyPI jest {}, but ensurepip "
                  "has {}".format(project, upstream_version, version))

    jeżeli outofdate:
        sys.exit(1)


jeżeli __name__ == "__main__":
    main()
