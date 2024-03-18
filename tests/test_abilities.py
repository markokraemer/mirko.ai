import os
from abilities import TerminalOps, RetrievalOps
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
    subject = TerminalOps.schema()
    assert_tool_fields(subject)
    verify(subject)

def test_retrieval_schema():
    subject = RetrievalOps.schema()
    assert_tool_fields(subject)
    verify(subject)

if os.getenv("INTEGRATION"):
    def test_send_ls():
        print(TerminalOps("workspace-dev-env-1").send_command("ls"))

    def test_list_tree():
        print(RetrievalOps("workspace-dev-env-1").get_file_tree(".", 2))