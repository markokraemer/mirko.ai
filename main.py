import json
from core.abilities import TerminalOps, RetrievalOps

# Load config
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Initialize with config values
terminal_ops = TerminalOps(config["container_id"])
retrieval_ops = RetrievalOps(config["base_path"])


def main():
    pass

if __name__ == "__main__":
    main()

