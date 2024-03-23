import os
import json
from core.tools import TerminalTool, RetrievalTool, get_container_merged_dir
from core.utils.file_utils import find_files
from approvaltests.approvals import verify

def assert_tool_fields(schema):
    """
    Check some basic fields on an OpenAI function call tool definition.
    If we wanted to be rigorious we could use the jsonschema, but this is a start.
    """
    for tool in schema: 
        assert tool['type'] == 'function'
        assert tool['function']
        assert tool['function']['name']
        assert tool['function']['description']
        assert tool['function']['parameters']

def test_terminal_schema():
    subject = TerminalTool.schema()
    assert_tool_fields(subject)
    verify(subject)

def test_retrieval_schema():
    subject = RetrievalTool.schema()
    assert_tool_fields(subject)
    verify(subject)


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

def test_retrieval_Tool_read_file_contents(fs):
    fs.create_file("/var/fakedata/a.txt", contents="..contents..")
    subject = RetrievalTool("/var/fakedata")
    found = subject.read_file_contents("a.txt")
    assert found.ok, found.output
    assert found.output == '..contents..'

if os.getenv("INTEGRATION"):
    def test_send_ls():
        print(TerminalTool("workspace-dev-env-1").send_command("ls"))

    def test_list_tree():
        base_path = get_container_merged_dir("workspace-dev-env-1")
        subject = RetrievalTool(base_path)
        print(subject.get_file_tree(".", 2))

        