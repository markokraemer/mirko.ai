import os
import pytest
from abilities import TerminalOps, RetrievalOps, get_container_merged_dir
from abilities.file_util import find_files
from approvaltests.approvals import verify


def test_schema_terminal():
    verify(TerminalOps.schema())

def test_schema_retrieval():
    verify(RetrievalOps.schema())


def test_find_files(fs):
    # The fs fixture is pyfakefs
    fs.create_file("/var/fakedata/a/xx1.txt")
    fs.create_file("/var/fakedata/a/.DS_Store") # Excluded
    
    found = find_files("/var/fakedata", 1)
    assert found == ["a/xx1.txt"]

def test_find_files_depth_limit(fs):
    fs.create_file("/var/fakedata/a/b/xx1.txt")
    found = find_files("/var/fakedata", 1)
    assert found == []

def test_find_files_exclude_ext(fs):
    fs.create_file("/var/fakedata/xx1.jpg")
    found = find_files("/var/fakedata", 1)
    assert found == []

def test_find_files_exclude_dirname(fs):
    fs.create_file("/var/fakedata/node_modules/xx1.jpg")
    found = find_files("/var/fakedata", 3)
    assert found == []



if os.getenv("INTEGRATION"):
    def test_send_ls():
        print(TerminalOps("workspace-dev-env-1").send_command("ls"))

    def test_list_tree():
        base_path = get_container_merged_dir("workspace-dev-env-1")
        print(base_path)
        subject = RetrievalOps(base_path)
        print(subject.get_file_tree(".", 2))
        