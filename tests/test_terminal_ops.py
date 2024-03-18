import os
from abilities import TerminalOps
from approvaltests.approvals import verify


def test_schema():
    verify(TerminalOps.schema())

if os.getenv("INTEGRATION"):
    def test_integration():
        print(TerminalOps("workspace-dev-env-1").send_command("ls"))
