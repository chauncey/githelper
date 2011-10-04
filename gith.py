#!/usr/bin/env python2.6
"""Helper for git stat/diff in git checkouts with BBx files"""

import os, sys, re, subprocess
from optparse import OptionParser

PATHS = {'cgi-bin': 'cgi-bin/pgms/'
       , 'pgms': 'pgms/'
       , 'scripts': '../cgi-bin/pgms/'}

REGX = re.compile("\w+\.lst")
CMDS = {'s': 'status', 'd': 'diff', 'c': 'commit'}
#CMDS = ['stat','diff','commit']


def upmaster():
    """Checkout master and update"""
    print subprocess.Popen("git checkout master"
            , shell=True
            , stdin=subprocess.PIPE
            , stdout=subprocess.PIPE).communicate()[0].strip()
    print subprocess.Popen("svn up", shell=True
            , stdin=subprocess.PIPE
            , stdout=subprocess.PIPE).communicate()[0].strip()
    print subprocess.Popen("git commit -am 'Outside changes'"
            , shell=True
            , stdin=subprocess.PIPE
            , stdout=subprocess.PIPE).communicate()[0].strip()



class GitHelper(object):
    """Help git with BBx files"""

    def __init__(self, cmd=None, debug=False):
        """Take an incoming command if we have one"""
        self.path = None
        self.msg = ''
        self.cmd = cmd
        if not self.cmd:
            self.cmd = "s"
        self.debug = False
        if debug:
            self.debug = True

    def handle(self):
        """Handle options"""
        dirs = os.listdir("./")

        if self.cmd != "m":
            if self.findpath(dirs):
                # Poke stuff
                for x in os.listdir(self.path):
                    if os.path.isfile(os.path.join(self.path, x)) \
                            and not REGX.search(x):
                        self.pokeit(x)
            scmd = "git  %s" % CMDS.get(self.cmd)
            s = subprocess.Popen( scmd
                                , shell=True
                                , stdin=subprocess.PIPE
                                , stdout=subprocess.PIPE )
            self.msg += s.communicate()[0]
        else:
            upmaster()
            self.mergemaster()
            self.msg +=  "Complete"
        return self.msg

    def findpath(self, dirs):
        """find the right path"""
        if "pgms" in os.listdir("../"):
            self.path = "./"

        for i in dirs:
            if i in PATHS:
                self.path = PATHS.get(i)

        if not self.path:
            self.msg += "No BBx programs found in this checkout"
            return False
        else:
            return True

    def pokeit(self, file_):
        """poke a file"""
        pcmd = "poke.py cp -l %s %s" % \
                  (os.path.join(self.path, file_), self.path)
        if self.debug:
            print pcmd
        p = subprocess.Popen(pcmd
                           , shell=True
                           , stdin=subprocess.PIPE
                           , stdout=subprocess.PIPE)
        res = p.communicate()[0]
        if self.debug:
            print res

    def mergemaster(self):
        """Merge all branches with master"""
        cmd = "git checkout %s; git merge master"
        subprocess.Popen(["git", "checkout", "master"]
                , stdin=subprocess.PIPE
                , stdout=subprocess.PIPE).communicate()
        branches = subprocess.Popen(["git", "branch"]
                , stdin=subprocess.PIPE
                , stdout=subprocess.PIPE).communicate()[0].split()
        for b in branches:
            if b not in ("*","master"):
                res = subprocess.Popen(cmd % b
                        , shell=True
                        , stdin=subprocess.PIPE
                        , stdout=subprocess.PIPE).communicate()[0]
                if self.debug:
                    print res.strip()
        subprocess.Popen(["git", "checkout", "master"]
                , stdin=subprocess.PIPE
                , stdout=subprocess.PIPE).communicate()


def check_gitrepo():
    """Check that this is run inside a git repo"""
    p = subprocess.Popen("git status"
                        , shell=True
                        , stdin=subprocess.PIPE
                        , stdout=subprocess.PIPE)
    res = p.communicate()[0]
    if res[:5] == u"fatal":
        return False
    else:
        return True

if "__main__" == __name__:

    if not check_gitrepo():
        print "You must be in a Git Checkout to run this script."
        sys.exit(0)

    # get whatever from the command line
    oparser = OptionParser()
    oparser.add_option("-s", "--status"
                      , action = "store_const"
                      , const = "s"
                      , dest = "cmd"
                      , help = "Git status")
    oparser.add_option("-d", "--diff"
                      , action = "store_const"
                      , const = "d"
                      , dest = "cmd"
                      , help = "Interactive search (default)")
    oparser.add_option("-m", "--mergebranches"
                      , action = "store_const"
                      , const = "m"
                      , dest = "cmd"
                      , help = "Merge all branches with master")
    oparser.add_option("--debug"
                      , action = "store_true"
                      , dest = "debug"
                      , default=False
                      , help = "Debug mode")
    (options, args) = oparser.parse_args()

    g = GitHelper(options.cmd, options.debug)
    print g.handle()

