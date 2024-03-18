import os
from abilities import TerminalOps, RetrievalOps
from approvaltests.approvals import verify


def test_schema_terminal():
    verify(TerminalOps.schema())

def test_schema_retrieval():
    verify(RetrievalOps.schema())

if os.getenv("INTEGRATION"):
    def test_send_ls():
        print(TerminalOps("workspace-dev-env-1").send_command("ls"))

    def test_list_tree():
        print(RetrievalOps("workspace-dev-env-1").get_file_tree(".", 2))