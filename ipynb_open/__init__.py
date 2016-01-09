# -*- coding: utf-8 -*-

import os.path as op
import psutil


def _abspath(path):
    return op.abspath(op.expanduser(path))


def gather_notebooks():
    """ Gather processes of IPython Notebook

    Return
    ------
    notes : list of dict
        each dict has following keys: "pid", "cwd", and "port"

    Raises
    ------
    RuntimeError
        - No IPython Notebook servers are found

    """
    notes = []
    for p in psutil.process_iter():
        if not p.name().lower() in ["ipython", "python"]:
            continue
        if "notebook" not in p.cmdline():
            continue
        for net in p.connections(kind="inet4"):
            if net.status != "LISTEN":
                continue
            _, port = net.laddr
            break
        notes.append({
            "pid": p.pid,
            "cwd": p.cwd(),
            "port": port,
        })
    if not notes:
        raise RuntimeError("No IPython Notebook found")
    return notes


def resolve_url(ipynb_path, notebooks=None):
    """
    Return valid URL for .ipynb

    Parameters
    ----------
    ipynb_path : str
        path of existing .ipynb file

    Raises
    ------
    RuntimeError
        - Existing notebook servers do not start
          on the parent directory of .ipynb file.
    """
    ipynb_path = _abspath(ipynb_path)
    if not notebooks:
        notebooks = gather_notebooks()
    for note in notebooks:
        cwd = note["cwd"]
        if cwd.endswith("/"):
            cwd = cwd[:-1]
        if not ipynb_path.startswith(cwd):
            continue
        note["postfix"] = ipynb_path[len(cwd) + 1:]  # remove '/'
        return "http://localhost:{port}/notebooks/{postfix}".format(**note)
    raise RuntimeError("No valid Notebook found. "
                       "Please start notebook server first.")
