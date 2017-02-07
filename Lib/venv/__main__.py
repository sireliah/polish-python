zaimportuj sys
z . zaimportuj main

rc = 1
spróbuj:
    main()
    rc = 0
wyjąwszy Exception jako e:
    print('Error: %s' % e, file=sys.stderr)
sys.exit(rc)
