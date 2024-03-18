from abilities import TerminalOps


if __name__ == "__main__":
    print(TerminalOps("workspace-dev-env-1").send_command("ls"))
    print(TerminalOps.schema())

# For now, running with:
# python -m test.test_workspace_integration
