import numpy as np
import tkinter as tk
import itertools


win = tk.Tk()
win.geometry("700x500")
win.title("Functional Dependency Calculator")


class FDs:
    FDIsKey = 'CK'
    FDIsSuperkey = 'SK'

    def __init__(self, attributes=None, fds=None):
        self.attributes = set()
        self.fds = []

        if attributes:
            if type(attributes) is not str:
                raise TypeError("Invalid datatype for attributes")

            self.attributes = {x for x in attributes}

        if fds:
            if type(fds) is not list:
                raise TypeError("Invalid datatype for fds")
            for f in fds:
                self.addfd(f)
        return

    def addfd(self, f):
        if type(f) is not tuple:
            raise TypeError("Invalid datatype for an fd")

        if type(f[0]) is not set:
            raise TypeError("Invalid datatype for an fd")

        if type(f[1]) is not set:
            raise TypeError("Invalid datatype for an fd")

        self.attributes = self.attributes.union(f[0])
        self.attributes = self.attributes.union(f[1])

        nx = f[1].difference(f[0])

        if len([x for x in self.fds if x[0] == f[0]]) > 0:
            for x in self.fds:
                if x[0] == f[0]:
                    # eliminate the FDs that already exist.
                    nx = nx.difference(x[1])

        for x in nx:
            self.fds.append([f[0], set(x)])
        return

    def consolidate(self):
        retval = []
        for f in self.fds:
            if len([x for x in retval if x[0] == f[0]]) > 0:
                for x in retval:
                    if x[0] == f[0]:
                        x[1] = x[1].union(f[1])
                        break
            else:
                retval.append(f.copy())
        return retval

    def attrclosure(self, ta):
        a = {x for x in ta} if type(ta) is not set else ta
        r = a.copy()
        oldr = None
        while oldr != r:
            oldr = r
            for f in self.fds:
                if f[0].issubset(r):
                    r = r.union(f[1])

        return(r.difference(a))

    def fdclosure(self):
        retval = []
        allkeys = self.keys()

        for l in range(0, len(self.attributes)):
            for k in itertools.combinations(self.attributes, l+1):
                r = self.attrclosure(k)
                if len(r) > 0:
                    if k in allkeys:
                        iskey = self.FDIsKey
                    elif self.attrclosure(k).union(k) == self.attributes:
                        iskey = self.FDIsSuperkey
                    else:
                        iskey = None
                    retval.append((set(k), r, iskey))
        return(retval)

    def keys(self):
        keys = []
        for l in range(0, len(self.attributes)):
            for c in itertools.combinations(self.attributes, l+1):
                if len([k for k in keys if set(k).intersection(c) ==
                        set(k)]) > 0:
                    continue
                if self.attrclosure(c).union(c) == self.attributes:
                    keys.append(c)
        return keys

    def printkeys(self):
        for ck in self.keys():
            ck_label['text'] += '\n' + ''.join(ck)

    def minimalCover(self):
        # the minimal cover is defined as the smallest set of FDs that
        # have the same closure as a given set of FDs.
        fdc = self.fdclosure()
        for ix in range(len(self.fds)-1, -1, -1):
            f = self.fds[ix].copy()
            del self.fds[ix]
            fdc1 = self.fdclosure()
            if fdc1 == fdc:
                continue
            self.fds.append(f)
        for fd in self.consolidate():
            for i in range(len(fd)-1):
                mincover_label['text'] += '\n' + ''.join(fd[i]) + '->' + ''.join(fd[i+1])

    def isbcnf(self):
        for c in self.fdclosure():
            if c[2] is not None:
                continue
            return False
        return True

    def is3nf(self):
        if self.isbcnf():
            return True
        allkeys = self.keys()
        for c in self.fdclosure():
            if c[2] is not None:
                continue
            if len([k for k in allkeys if c[1].issubset(k)]) > 0:
                # this FD is to an RHS which is a subset of a key
                continue
            return False
        return True

    @staticmethod
    def mkfd(l, r):
        a = {x for x in l}
        b = {x for x in r}

        return((a, b))


def calculate2():
    f = FDs()
    x = []
    y = []
    fd_list = fd_text.get(1.0, "end-1c").replace(' ', '').splitlines()
    for line in fd_list:
        temp = line.split("->")
        x.append(temp[0])
        y.append(temp[1])
    for i in range(len(fd_list)):
        f.addfd(FDs.mkfd(x[i], y[i]))
    f.printkeys()
    f.minimalCover()
    nf3_label['text'] += '\n' + str(f.is3nf())
    bcnf_label['text'] += '\n' + str(f.isbcnf())
    s = ''
    for fdc in f.fdclosure():
        s += '\n' + "{" + "".join(fdc[0]) + "}+" + " = " + "".join(fdc[0]) + "".join(fdc[1]) + (" -> " if fdc[2] != None else  "") + (fdc[2] or "")
    closure_label['text'] += s


fd_label = tk.Label(win, text="Enter FDs: ", font=("default", 12))
fd_label.grid(row=0, column=0)
fd_text = tk.Text(win, height=10, width=10, font=("default", 12))
fd_text.grid(row=0, column=1)

fd_button = tk.Button(win, text="Calculate", command=calculate2, font=("default", 12))
fd_button.grid(row=0, column=2)

closure_label = tk.Label(win, text="|  Attribute Closures  ", font=("default", 12))
closure_label.grid(row=2, column=0, sticky='N')

ck_label = tk.Label(win, text="|    Candidate Key", font=("default", 12))
ck_label.grid(row=2, column=1, sticky='N')

mincover_label = tk.Label(win, text="|    Canonical Closures", font=("default", 12))
mincover_label.grid(row=2, column=2, sticky='N')

nf3_label = tk.Label(win, text="|    Is 3NF?  ", font=("default", 12))
nf3_label.grid(row=2, column=3, sticky='N')

bcnf_label = tk.Label(win, text="|    Is BCNF?  |", font=("default", 12))
bcnf_label.grid(row=2, column=4, sticky='N')
win.mainloop()
