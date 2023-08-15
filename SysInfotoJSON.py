import json
import subprocess
import platform
import paramiko

def get_system_info():
    local_info = get_local_system_info()
    remote_info = get_remote_system_info()

    system_info = {
        "Local": local_info,
        "Remote": remote_info,
    }
    return system_info

def get_local_system_info():
    local_info = {
        "system": "",
        "node": "",
        "release": "",
        "version": "",
        "processor": "",
        "architecture": "",
        "uptime": "",
    }

    local_system = platform.uname()
    local_info["system"] = local_system.system
    local_info["node"] = local_system.node
    local_info["release"] = local_system.release
    local_info["version"] = get_local_os_version()
    local_info["processor"] = get_processor_info()
    local_info["architecture"] = get_architecture_info()
    local_info["uptime"] = get_system_uptime()

    return local_info

def get_local_os_version():
    try:
        with open("/etc/os-release", "r") as os_release_file:
            lines = os_release_file.readlines()
            version_id = None
            distribution = None
            for line in lines:
                if line.startswith("VERSION_ID"):
                    version_id = line.split("=")[1].strip().strip('"')
                elif line.startswith("ID"):
                    distribution = line.split("=")[1].strip().strip('"')
                if version_id and distribution:
                    return f"{distribution} {version_id}"
            return "N/A"
    except Exception as e:
        return "N/A"

def get_processor_info():
    try:
        output = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | uniq", shell=True, universal_newlines=True)
        processor_info = output.split(":")[1].strip()
        return processor_info
    except Exception as e:
        return "N/A"

def get_architecture_info():
    try:
        output = subprocess.check_output("uname -m", shell=True, universal_newlines=True)
        architecture_info = output.strip()
        return architecture_info
    except Exception as e:
        return "N/A"

def get_system_uptime():
    try:
        output = subprocess.check_output("uptime -p", shell=True, universal_newlines=True)
        return output.strip()
    except Exception as e:
        return "N/A"


def get_remote_system_info():
    remote_info = {}
    
    # Remote server information
    remote_host = "x.x.x.x"
    remote_user = "user"
    private_key_path = "/path/to/private/key"  # Update the key path
    remote_port = 69  # Replace with your non-standard SSH port

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_key = paramiko.Ed25519Key(filename=private_key_path)  # Use Ed25519Key
        ssh_client.connect(remote_host, port=remote_port, username=remote_user, pkey=private_key)

        remote_info = get_remote_system_info_on_server(ssh_client)

        ssh_client.close()
    except Exception as e:
        print("Error:", e)

    return remote_info

def get_remote_system_info_on_server(ssh_client):
    remote_info = {}

    try:
        stdin, stdout, stderr = ssh_client.exec_command("uname -a")
        system_info = stdout.read().decode().strip().split()

        remote_info["system"] = system_info[0]
        remote_info["node"] = system_info[1]
        remote_info["release"] = system_info[2]
        remote_info["version"] = get_remote_os_version(ssh_client)
        remote_info["processor"] = get_remote_processor_info(ssh_client)
        remote_info["architecture"] = get_remote_architecture_info(ssh_client)
        remote_info["uptime"] = get_remote_system_uptime(ssh_client)

    except Exception as e:
        print("Error:", e)

    return remote_info

def get_remote_os_version(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("cat /etc/os-release | grep 'VERSION_ID' | cut -d '=' -f 2")
        version_id = stdout.read().decode().strip().strip('"')

        stdin, stdout, stderr = ssh_client.exec_command("cat /etc/os-release | grep 'ID' | grep -v 'VERSION' | cut -d '=' -f 2")
        distribution = stdout.read().decode().strip().strip('"')

        if distribution and version_id:
            return f"{distribution} {version_id}"
        return "N/A"
    except Exception as e:
        return "N/A"

def get_remote_processor_info(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("cat /proc/cpuinfo | grep 'model name' | uniq")
        processor_info = stdout.read().decode().strip().split(":")[1].strip()
        return processor_info
    except Exception as e:
        return "N/A"

def get_remote_architecture_info(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("uname -m")
        architecture_info = stdout.read().decode().strip()
        return architecture_info
    except Exception as e:
        return "N/A"

def get_remote_system_uptime(ssh_client):
    try:
        stdin, stdout, stderr = ssh_client.exec_command("uptime -p")
        uptime_info = stdout.read().decode().strip()
        return uptime_info
    except Exception as e:
        return "N/A"

def save_to_json(data):
    with open("system_info.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    system_info = get_system_info()
    save_to_json(system_info)
    print("System information saved to system_info.json")
