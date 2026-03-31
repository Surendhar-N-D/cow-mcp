from urllib.parse import urlparse
import asyncio
import resource

from constants import constants
from mcpconfig.config import mcp
from utils.debug import logger

MAX_CURL_RESPONSE_BYTES = 1024 * 1024
MAX_CURL_RESPONSE_CHARS = 20000
MAX_SHELL_OUTPUT_BYTES = 1024 * 1024
MAX_SHELL_OUTPUT_CHARS = 20000
DEFAULT_CURL_TIMEOUT_SECONDS = 30.0
DEFAULT_SHELL_TIMEOUT_SECONDS = 30.0

# DISALLOWED_CURL_FLAGS = {
#     "-K",
#     "--config",
#     "-o",
#     "--output",
#     "-O",
#     "--remote-name",
#     "--remote-name-all",
#     "-T",
#     "--upload-file",
#     "-F",
#     "--form",
#     "--form-string",
#     "-e",
#     "--referer",
#     "-E",
#     "--cert",
#     "--key",
#     "--proxy",
#     "-x",
#     "--preproxy",
#     "--interface",
#     "--resolve",
#     "--connect-to",
#     "--libcurl",
#     "--dump-header",
#     "-D",
#     "--stderr",
#     "--trace",
#     "--trace-ascii",
#     "--trace-config",
#     "--trace-ids",
#     "--trace-time",
#     "--unix-socket",
#     "--aws-sigv4",
#     "--oauth2-bearer",
#     "--ntlm",
#     "--negotiate",
# }

# DISALLOWED_SHELL_TOKENS = {"|", "||", "&&", ";", ">", ">>", "<", "<<", "`"}
# DISALLOWED_SHELL_COMMANDS = {
#     "rm",
#     "sudo",
#     "su",
#     "chmod",
#     "chown",
#     "dd",
#     "mkfs",
#     "fdisk",
#     "shutdown",
#     "reboot",
#     "poweroff",
#     "kill",
#     "killall",
#     "pkill",
#     "wget",
#     "env"
# }


# def _truncate_text(value: str, max_chars: int) -> tuple[str, bool]:
#     if len(value) <= max_chars:
#         return value, False
#     return value[:max_chars], True


# def _get_truncation_message(byte_truncated: bool, char_truncated: bool, max_bytes: int, max_chars: int) -> str:
#     if byte_truncated:
#         return f"Response truncated due to size limit ({max_bytes} bytes)."
#     if char_truncated:
#         return f"Response truncated due to character limit ({max_chars} characters)."
#     return ""


# def _clean_response_text(value: str) -> str:
#     value = re.sub(r"(?is)<script\b.*?>.*?</script>", "", value)
#     value = re.sub(r"(?is)<style\b.*?>.*?</style>", "", value)
#     value = re.sub(r"(?is)<noscript\b.*?>.*?</noscript>", "", value)
#     return re.sub(r"(?is)</?(script|style|noscript)\b[^>]*>", "", value)


# def _parse_http_request(curl_command: str) -> dict:
#     raw_input = curl_command.strip()
#     if not raw_input:
#         raise ValueError("curl_command cannot be empty")

#     if raw_input.startswith("http://") or raw_input.startswith("https://"):
#         parsed_url = urlparse(raw_input)
#         if not parsed_url.netloc:
#             raise ValueError("A valid absolute URL is required")
#         return {
#             "method": "GET",
#             "url": raw_input,
#             "headers": {},
#             "body": None,
#             "follow_redirects": False,
#             "verify": True,
#             "timeout": DEFAULT_CURL_TIMEOUT_SECONDS,
#         }

#     try:
#         tokens = shlex.split(raw_input, posix=True)
#     except ValueError as exc:
#         raise ValueError(f"Unable to parse curl command: {exc}") from exc

#     if not tokens:
#         raise ValueError("curl_command cannot be empty")

#     if tokens[0] != "curl":
#         raise ValueError("Command must start with 'curl'")

#     for token in tokens[1:]:
#         if any(token == flag or token.startswith(f"{flag}=") for flag in DISALLOWED_CURL_FLAGS):
#             raise ValueError(f"curl option not allowed: {token}")

#     try:
#         context = uncurl.parse_context(raw_input)
#     except Exception as exc:
#         raise ValueError(f"Unable to parse curl command: {exc}") from exc

#     method = str(getattr(context, "method", "GET")).upper()
#     url = getattr(context, "url", "")
#     headers = dict(getattr(context, "headers", {}) or {})
#     body = getattr(context, "data", None)

#     if method not in {"GET", "POST", "PUT"}:
#         raise ValueError(f"HTTP method not allowed: {method}")

#     if not url:
#         raise ValueError("curl command must include an http or https URL")

#     parsed_url = urlparse(url)
#     if not parsed_url.netloc:
#         raise ValueError("A valid absolute URL is required")

#     return {
#         "method": method,
#         "url": url,
#         "headers": headers,
#         "body": body,
#         "follow_redirects": "-L" in tokens or "--location" in tokens,
#         "verify": True,
#         "timeout": DEFAULT_CURL_TIMEOUT_SECONDS,
#     }

# def _parse_shell_command(command: str) -> list[str]:
#     raw_input = command.strip()
#     if not raw_input:
#         raise ValueError("command cannot be empty")

#     try:
#         tokens = shlex.split(raw_input, posix=True)
#     except ValueError as exc:
#         raise ValueError(f"Unable to parse command: {exc}") from exc

#     if not tokens:
#         raise ValueError("command cannot be empty")

#     # for token in tokens:
#     #     if token in DISALLOWED_SHELL_TOKENS:
#     #         raise ValueError(f"Shell operator not allowed: {token}")

#     # if tokens[0] in DISALLOWED_SHELL_COMMANDS:
#     #     raise ValueError(f"Command not allowed: {tokens[0]}")

#     return tokens


# if constants.ENABLE_CURL_EXECUTION:
#     # @mcp.tool()
#     async def execute_curl(curl_command: str) -> dict:
#         """
#         Execute a URL or curl command through httpx.

#         Args:
#             curl_command: Either a plain site URL or a curl command.

#         Returns:
#             Dictionary containing the response body or execution error.
#         """
#         try:
#             request_config = _parse_http_request(curl_command)
#             logger.debug(
#                 "execute_curl parsed request: method=%s url=%s follow_redirects=%s",
#                 request_config["method"],
#                 request_config["url"],
#                 request_config["follow_redirects"],
#             )
#         except ValueError as exc:
#             logger.warning("execute_curl rejected command: %s", exc)
#             return {
#                 "error": str(exc),
#                 "curl_command": curl_command,
#                 "sanitized": False,
#             }

#         try:
#             logger.info("execute_curl sending request to %s", request_config["url"])
#             collected = bytearray()
#             truncated = False

#             async with httpx.AsyncClient(
#                 timeout=httpx.Timeout(request_config["timeout"]),
#                 verify=request_config["verify"],
#             ) as client:
#                 async with client.stream(
#                 method=request_config["method"],
#                 url=request_config["url"],
#                 headers=request_config["headers"],
#                 content=request_config["body"],
#                 follow_redirects=request_config["follow_redirects"],
#             ) as response:
#                     async for chunk in response.aiter_bytes():
#                         remaining = MAX_CURL_RESPONSE_BYTES - len(collected)
#                         if remaining <= 0:
#                             truncated = True
#                             break
#                         if len(chunk) > remaining:
#                             collected.extend(chunk[:remaining])
#                             truncated = True
#                             break
#                         collected.extend(chunk)

#                     cleaned_data = _clean_response_text(
#                         bytes(collected).decode("utf-8", errors="replace")
#                     )
#                     data, char_truncated = _truncate_text(
#                         cleaned_data,
#                         MAX_CURL_RESPONSE_CHARS,
#                     )
#                     logger.debug(
#                         "execute_curl completed: status_code=%s bytes=%s truncated=%s",
#                         response.status_code,
#                         len(collected),
#                         truncated or char_truncated,
#                     )

#                     return {
#                         "sanitized": True,
#                         "status_code": response.status_code,
#                         "headers": dict(response.headers),
#                         "data": data,
#                         "truncated": truncated or char_truncated,
#                         "message": _get_truncation_message(
#                             truncated,
#                             char_truncated,
#                             MAX_CURL_RESPONSE_BYTES,
#                             MAX_CURL_RESPONSE_CHARS,
#                         ),
#                         "max_response_bytes": MAX_CURL_RESPONSE_BYTES,
#                         "max_response_chars": MAX_CURL_RESPONSE_CHARS,
#                     }
#         except httpx.TimeoutException:
#             logger.warning("execute_curl timed out for input: %s", curl_command)
#             return {"error": "Request timed out", "sanitized": True}
#         except httpx.HTTPError as exc:
#             logger.error("execute_curl failed: %s", exc)
#             return {"error": f"Request failed: {str(exc)}", "sanitized": True}
#         except Exception as exc:
#             logger.error("execute_curl unexpected error: %s", exc)
#             return {"error": f"Unexpected execute_curl error: {str(exc)}", "sanitized": True}



# if constants.ENABLE_SHELL_EXECUTION:
# @mcp.tool()
# async def execute_shell_command(command: str) -> dict:
#     """
#     Execute a shell command safely without invoking a shell.

#     Args:
#         command: Command string to execute.

#     Returns:
#         Dictionary containing stdout, stderr, exit code, or an error.
#     """
#     try:
#         tokens = _parse_shell_command(command)
#         logger.debug("execute_shell_command parsed command: %s", tokens)
#     except ValueError as exc:
#         logger.warning("execute_shell_command rejected command: %s", exc)
#         return {
#             "error": str(exc),
#             "command": command,
#             "sanitized": False,
#         }

#     process = None
#     try:
#         logger.info("execute_shell_command running: %s", tokens[0])
#         process = await asyncio.create_subprocess_exec(
#             *tokens,
#             shell=True,
#             stdout=asyncio.subprocess.PIPE,
#             stderr=asyncio.subprocess.PIPE,
#         )
#         stdout, stderr = await asyncio.wait_for(
#             process.communicate(),
#             timeout=DEFAULT_SHELL_TIMEOUT_SECONDS,
#         )
#     except asyncio.TimeoutError:
#         if process is not None:
#             process.kill()
#             await process.communicate()
#         logger.warning("execute_shell_command timed out for command: %s", command)
#         return {"error": "Command timed out", "sanitized": True}
#     except Exception as exc:
#         logger.error("execute_shell_command failed: %s", exc)
#         return {"error": f"Failed to execute command: {str(exc)}", "sanitized": True}

#     stdout_bytes = stdout[:MAX_SHELL_OUTPUT_BYTES]
#     stderr_bytes = stderr[:MAX_SHELL_OUTPUT_BYTES]
#     stdout_text, stdout_char_truncated = _truncate_text(
#         stdout_bytes.decode("utf-8", errors="replace"),
#         MAX_SHELL_OUTPUT_CHARS,
#     )
#     stderr_text, stderr_char_truncated = _truncate_text(
#         stderr_bytes.decode("utf-8", errors="replace"),
#         MAX_SHELL_OUTPUT_CHARS,
#     )
#     stdout_byte_truncated = len(stdout) > MAX_SHELL_OUTPUT_BYTES
#     stderr_byte_truncated = len(stderr) > MAX_SHELL_OUTPUT_BYTES
#     logger.debug(
#         "execute_shell_command completed: exit_code=%s stdout_bytes=%s stderr_bytes=%s truncated=%s",
#         process.returncode,
#         len(stdout),
#         len(stderr),
#         stdout_byte_truncated or stderr_byte_truncated or stdout_char_truncated or stderr_char_truncated,
#     )

#     return {
#         "sanitized": True,
#         "exit_code": process.returncode,
#         "stdout": stdout_text,
#         "stderr": stderr_text,
#         "truncated": (
#             stdout_byte_truncated
#             or stderr_byte_truncated
#             or stdout_char_truncated
#             or stderr_char_truncated
#         ),
#         "message": _get_truncation_message(
#             stdout_byte_truncated or stderr_byte_truncated,
#             stdout_char_truncated or stderr_char_truncated,
#             MAX_SHELL_OUTPUT_BYTES,
#             MAX_SHELL_OUTPUT_CHARS,
#         ),
#         "max_output_bytes": MAX_SHELL_OUTPUT_BYTES,
#         "max_output_chars": MAX_SHELL_OUTPUT_CHARS,
#     }

# Constants
MAX_OUTPUT_CHARS = 20000   # Maximum characters to return
CMD_TIMEOUT = 30  

@mcp.tool()
async def execute_shell_command(cmd: str) -> str:
    """
    Run a shell command asynchronously with:
      - Non-root user (sudo -u mcpuser)
      - Resource limits
      - Output limited to MAX_OUTPUT_CHARS
      - Timeout defined by CMD_TIMEOUT
      - Firejail isolation (optional)
    Returns combined stdout+stderr truncated to MAX_OUTPUT_CHARS
    """

    # if not is_allowed(cmd):
    #     return "Error: Command not allowed"

    # Preexec function for resource limits
    def limit_resources():
        # CPU time limit (seconds)
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        # Memory limit (bytes)
        resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
        # Limit number of open files
        resource.setrlimit(resource.RLIMIT_NOFILE, (16, 16))

    # Firejail + non-root execution
    full_cmd = [
        "sudo", "-u", "mcpuser",
        "firejail",
        "--quiet",
        "--private",
        "--net=all",
        "--caps.drop=all",
        "bash",
        "-c",
        cmd
    ]

    process = await asyncio.create_subprocess_exec(
        *full_cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        preexec_fn=limit_resources
    )

    stdout_total = []
    stderr_total = []
    output_chars = 0

    try:
        # Read stdout and stderr concurrently with timeout
        while True:
            try:
                stdout_line, stderr_line = await asyncio.wait_for(
                    asyncio.gather(
                        process.stdout.readline(),
                        process.stderr.readline()
                    ),
                    timeout=CMD_TIMEOUT
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stderr_total.append("\nCommand killed due to timeout.")
                break

            if not stdout_line and not stderr_line:
                break

            if stdout_line:
                text = stdout_line.decode(errors="replace")
                stdout_total.append(text)
                output_chars += len(text)

            if stderr_line:
                text = stderr_line.decode(errors="replace")
                stderr_total.append(text)
                output_chars += len(text)

            # Stop reading if we exceed MAX_OUTPUT_CHARS
            if output_chars >= MAX_OUTPUT_CHARS:
                break

        # Ensure process is terminated
        if process.returncode is None:
            process.kill()
            await process.wait()

    except Exception as e:
        stderr_total.append(f"\nError executing command: {e}")

    # Combine stdout + stderr and truncate
    combined_output = "".join(stdout_total + stderr_total)
    return combined_output[:MAX_OUTPUT_CHARS]
