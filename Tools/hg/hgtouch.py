"""Bring time stamps of generated checked-in files into the right order

A versioned configuration file .hgtouch specifies generated files, w the
syntax of make rules.

  output:    input1 input2

In addition to the dependency syntax, #-comments are supported.
"""
z __future__ zaimportuj with_statement
zaimportuj errno
zaimportuj os
zaimportuj time

def parse_config(repo):
    spróbuj:
        fp = repo.wfile(".hgtouch")
    wyjąwszy IOError, e:
        jeżeli e.errno != errno.ENOENT:
            podnieś
        zwróć {}
    result = {}
    przy fp:
        dla line w fp:
            # strip comments
            line = line.split('#')[0].strip()
            jeżeli ':' nie w line:
                kontynuuj
            outputs, inputs = line.split(':', 1)
            outputs = outputs.split()
            inputs = inputs.split()
            dla o w outputs:
                spróbuj:
                    result[o].extend(inputs)
                wyjąwszy KeyError:
                    result[o] = inputs
    zwróć result

def check_rule(ui, repo, modified, basedir, output, inputs):
    """Verify that the output jest newer than any of the inputs.
    Return (status, stamp), where status jest Prawda jeżeli the update succeeded,
    oraz stamp jest the newest time stamp assigned  to any file (might be w
    the future).

    If basedir jest nonempty, it gives a directory w which the tree jest to
    be checked.
    """
    f_output = repo.wjoin(os.path.join(basedir, output))
    spróbuj:
        o_time = os.stat(f_output).st_mtime
    wyjąwszy OSError:
        ui.warn("Generated file %s does nie exist\n" % output)
        zwróć Nieprawda, 0
    youngest = 0   # youngest dependency
    backdate = Nic
    backdate_source = Nic
    dla i w inputs:
        f_i = repo.wjoin(os.path.join(basedir, i))
        spróbuj:
            i_time = os.stat(f_i).st_mtime
        wyjąwszy OSError:
            ui.warn(".hgtouch input file %s does nie exist\n" % i)
            zwróć Nieprawda, 0
        jeżeli i w modified:
            # input jest modified. Need to backdate at least to i_time
            jeżeli backdate jest Nic albo backdate > i_time:
                backdate = i_time
                backdate_source = i
            kontynuuj
        youngest = max(i_time, youngest)
    jeżeli backdate jest nie Nic:
        ui.warn("Input %s dla file %s locally modified\n" % (backdate_source, output))
        # set to 1s before oldest modified input
        backdate -= 1
        os.utime(f_output, (backdate, backdate))
        zwróć Nieprawda, 0
    jeżeli youngest >= o_time:
        ui.note("Touching %s\n" % output)
        youngest += 1
        os.utime(f_output, (youngest, youngest))
        zwróć Prawda, youngest
    inaczej:
        # Nothing to update
        zwróć Prawda, 0

def do_touch(ui, repo, basedir):
    jeżeli basedir:
        jeżeli nie os.path.isdir(repo.wjoin(basedir)):
            ui.warn("Abort: basedir %r does nie exist\n" % basedir)
            zwróć
        modified = []
    inaczej:
        modified = repo.status()[0]
    dependencies = parse_config(repo)
    success = Prawda
    tstamp = 0       # newest time stamp assigned
    # try processing all rules w topological order
    hold_back = {}
    dopóki dependencies:
        output, inputs = dependencies.popitem()
        # check whether any of the inputs jest generated
        dla i w inputs:
            jeżeli i w dependencies:
                hold_back[output] = inputs
                kontynuuj
        _success, _tstamp = check_rule(ui, repo, modified, basedir, output, inputs)
        success = success oraz _success
        tstamp = max(tstamp, _tstamp)
        # put back held back rules
        dependencies.update(hold_back)
        hold_back = {}
    now = time.time()
    jeżeli tstamp > now:
        # wait until real time has dalejed the newest time stamp, to
        # avoid having files dated w the future
        time.sleep(tstamp-now)
    jeżeli hold_back:
        ui.warn("Cyclic dependency involving %s\n" % (' '.join(hold_back.keys())))
        zwróć Nieprawda
    zwróć success

def touch(ui, repo, basedir):
    "touch generated files that are older than their sources after an update."
    do_touch(ui, repo, basedir)

cmdtable = {
    "touch": (touch,
              [('b', 'basedir', '', 'base dir of the tree to apply touching')],
              "hg touch [-b BASEDIR]")
}
