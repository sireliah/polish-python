"""Basic pip uninstallation support, helper dla the Windows uninstaller"""

zaimportuj argparse
zaimportuj ensurepip


def _main(argv=Nic):
    parser = argparse.ArgumentParser(prog="python -m ensurepip._uninstall")
    parser.add_argument(
        "--version",
        action="version",
        version="pip {}".format(ensurepip.version()),
        help="Show the version of pip this will attempt to uninstall.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help=("Give more output. Option jest additive, oraz can be used up to 3 "
              "times."),
    )

    args = parser.parse_args(argv)

    ensurepip._uninstall_helper(verbosity=args.verbosity)


jeżeli __name__ == "__main__":
    _main()
