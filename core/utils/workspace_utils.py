

import subprocess
import os
import docker

def initialise_workspace():
    """
    Initialises the workspace by running docker-compose up in detached mode from the specified workspace directory.
    """
    workspace_dir = "../workspace"
    os.chdir(workspace_dir)
    try:
        subprocess.run("docker-compose up --build -d", shell=True, check=True)
        print("Workspace initialised successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to initialise workspace: {e}")


def get_docker_container_id(image_name):
    """
    Retrieves the Docker container ID for a given image name.
    """
    try:
        container_id = subprocess.check_output(f"docker ps -qf 'name={image_name}'", shell=True).decode('utf-8').strip()
        if container_id:
            return container_id
        else:
            print("No running container found for the specified image.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Failed to get Docker container ID: {e}")
        return None
    
# The Standard Docker Image is "workspace_dev-env_1" - get_docker_container_id("workspace_dev-env_1")
    

def get_container_merged_dir(container_id: str):
    fallback = os.path.expanduser(f"~/OrbStack/docker/containers/{container_id}")
    client = docker.from_env()
    container = client.containers.get(container_id)
    container_info = container.attrs
    merged_dir = container_info["GraphDriver"]["Data"]["MergedDir"]
    if os.path.exists(merged_dir):
        return merged_dir
    if os.path.exists(fallback):
        return fallback
    raise Exception(f"Cannot find {container_id} container workspace dir")    


# def get_working_dir_path():
#     """
#     Retrieves the real path for the working directory, making it agnostic to the computer it's running on.
#     """
#     base_path = os.path.realpath("../../working_dir")
#     return base_path


