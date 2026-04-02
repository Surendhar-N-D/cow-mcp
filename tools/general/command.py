import asyncio
import resource

from mcpconfig.config import mcp
from utils.debug import logger

MAX_OUTPUT_CHARS = 20000
CMD_TIMEOUT = 30
TRUNCATION_NOTICE = "\n\n[output truncated to 20,000 characters]"

@mcp.tool()
async def execute_shell_command(cmd: str) -> str:
    """
    Run a shell command in an isolated sandbox with resource limits and a 30s timeout.

    Output is capped at 20,000 characters per call. If more output is needed or filtering is
    required, use your own logic to retrieve, continue reading, store, and filter the data
    using a single command or a single pipeline.

    Returns combined stdout and stderr, truncated to 20000.
    """
    if not cmd or not cmd.strip():
        return "Command cannot be empty."

    def limit_resources():
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))

    bwrap_cmd = [
        "bwrap",
        "--die-with-parent",
        "--unshare-all",
        "--share-net",
        "--new-session",
        "--cap-drop", "ALL",
        "--clearenv",
        "--setenv", "PATH", "/usr/bin:/bin:/usr/local/bin",
        "--setenv", "HOME", "/tmp",
        "--setenv", "LANG", "C.UTF-8",
        "--tmpfs", "/tmp",
        "--ro-bind", "/usr", "/usr",
        "--ro-bind", "/bin", "/bin",
        "--ro-bind", "/lib", "/lib",
        "--ro-bind", "/usr/local", "/usr/local",
        "--ro-bind", "/etc", "/etc",
        # "--proc", "/proc",
        "--dev", "/dev",
        "--",
        "bash", "-c", cmd
    ]

    process = await asyncio.create_subprocess_exec(
        *bwrap_cmd,
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        preexec_fn=limit_resources
    )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            process.communicate(),
            timeout=CMD_TIMEOUT
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        logger.warning("execute_shell_command timed out after %ss", CMD_TIMEOUT)
        return "Command killed due to timeout."
    except FileNotFoundError:
        logger.exception("execute_shell_command failed: bwrap not found")
        return "Command execution failed: sandbox runtime."
    except Exception as e:
        logger.exception("execute_shell_command failed")
        return f"Error executing command: {e}"

    stdout_text = stdout_bytes.decode(errors="replace")
    stderr_text = stderr_bytes.decode(errors="replace")
    combined_output = stdout_text + stderr_text

    if len(combined_output) <= MAX_OUTPUT_CHARS:
        return combined_output

    allowed_chars = MAX_OUTPUT_CHARS - len(TRUNCATION_NOTICE)
    return combined_output[:allowed_chars] + TRUNCATION_NOTICE
