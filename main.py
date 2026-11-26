import os
import platform

from fastmcp import FastMCP

mcp = FastMCP(
    name="Computer Monitor",
    instructions="tools to get info about the operating system and the computer resources.",
)


def format_bytes(value: int) -> str:
    """convert bytes to a readable text like 12.34 GB"""
    size = float(value)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


@mcp.tool(
    name="cpuName",
    description="returns the name of the cpu used by the server.",
)
def cpu_name() -> str:
    try:
        with open("/proc/cpuinfo", "r") as file:
            for line in file:
                key = line.split(":")[0].strip().lower()
                if key in ("model name", "hardware", "model"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or "unknown"


@mcp.tool(
    name="availableRoot",
    description="returns the free space available in the root file system (/).",
)
def available_root() -> str:
    stats = os.statvfs("/")
    return format_bytes(stats.f_bavail * stats.f_frsize)


@mcp.tool(
    name="sizeRoot",
    description="returns the total size of the root file system (/).",
)
def size_root() -> str:
    stats = os.statvfs("/")
    return format_bytes(stats.f_blocks * stats.f_frsize)


@mcp.tool(
    name="kernelVersion",
    description="returns the version of the linux kernel that is running.",
)
def kernel_version() -> str:
    return os.uname().release


@mcp.tool(
    name="availableRAM",
    description="returns the amount of ram memory available in the system.",
)
def available_ram() -> str:
    with open("/proc/meminfo", "r") as file:
        for line in file:
            if line.startswith("MemAvailable:"):
                kilobytes = int(line.split()[1])
                return format_bytes(kilobytes * 1024)
    raise RuntimeError("could not read available ram.")


@mcp.tool(
    name="tasks",
    description="returns the number of tasks (processes) running in the system.",
)
def tasks() -> str:
    count = sum(1 for name in os.listdir("/proc") if name.isdigit())
    return f"{count} tasks"


@mcp.tool(
    name="systemLoad",
    description="returns the system load average for the last 1, 5 and 15 minutes.",
)
def system_load() -> dict[str, float]:
    load1, load5, load15 = os.getloadavg()
    return {
        "last_1_minute": round(load1, 2),
        "last_5_minutes": round(load5, 2),
        "last_15_minutes": round(load15, 2),
    }


def main() -> None:
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)


if __name__ == "__main__":
    main()