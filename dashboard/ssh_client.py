from django.conf import settings
import paramiko
import re
import logging

logger = logging.getLogger(__name__)


def run_command(command):
    try:
        # Load the key using the path from settings
        key = paramiko.RSAKey.from_private_key_file(str(settings.SSH_VM_KEY_PATH))
    except Exception as e:
        logger.error(f"Failed to load SSH private key: {e}")
        raise RuntimeError(f"Failed to load SSH private key: {e}")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    try:
        client.connect(
            hostname=settings.SSH_VM_HOST,
            username=settings.SSH_VM_USERNAME,
            pkey=key,
            timeout=10  # Add timeout to prevent hanging on connection failure
        )
    except Exception as e:
        logger.error(f"Failed to connect to VM via SSH ({settings.SSH_VM_HOST}): {e}")
        client.close()
        raise ConnectionError(f"SSH connection failed: {e}")

    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
    except Exception as e:
        logger.error(f"Failed to execute command '{command}': {e}")
        raise RuntimeError(f"Command execution failed: {e}")
    finally:
        client.close()

    return output



def get_ram_usage():
    output = run_command("free -m")

    lines = output.splitlines()

    memory_line = lines[1].split()

    total = int(memory_line[1])
    used = int(memory_line[2])

    ram_percent = (used / total) * 100

    return round(ram_percent, 2)


def get_disk_usage():
    output = run_command("df -h /")

    lines = output.splitlines()

    disk_line = lines[1].split()

    return float(
        disk_line[4].replace("%", "")
    )


def get_uptime_hours():
    output = run_command("cat /proc/uptime")

    seconds = float(
        output.split()[0]
    )

    return round(
        seconds / 3600,
        2
    )


def get_cpu_usage():
    output = run_command(
        "top -bn1 | grep '%Cpu'"
    )

    match = re.search(
        r'(\d+\.\d+)\s*id',
        output
    )

    if match:
        idle = float(match.group(1))
        return round(
            100 - idle,
            2
        )

    return 0.0


def get_remote_metrics():
    return {
        "cpu": get_cpu_usage(),
        "ram": get_ram_usage(),
        "disk": get_disk_usage(),
        "uptime": get_uptime_hours()
    }


if __name__ == "__main__":
    metrics = get_remote_metrics()

    print("\nAzure VM Metrics")
    print("----------------")
    print(f"CPU Usage   : {metrics['cpu']}%")
    print(f"RAM Usage   : {metrics['ram']}%")
    print(f"Disk Usage  : {metrics['disk']}%")
    print(f"Uptime      : {metrics['uptime']} hours")