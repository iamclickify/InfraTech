import paramiko
import re


HOST = "4.213.48.203"
USERNAME = "shubham"
KEY_FILE = "/app/ssh_keys/devops-ubuntu_key.pem"

def run_command(command):
    key = paramiko.RSAKey.from_private_key_file(KEY_FILE)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    client.connect(
        hostname=HOST,
        username=USERNAME,
        pkey=key
    )

    stdin, stdout, stderr = client.exec_command(command)

    output = stdout.read().decode()

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