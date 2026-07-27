#!/usr/bin/env python3
"""A small client for the local training MUD.

Defaults are intentionally usable for this exercise. Override them with command
line flags or MUD_HOST, MUD_PORT, MUD_USERNAME, and MUD_PASSWORD.
"""

from __future__ import annotations

import argparse
import os
import select
import socket
import sys
import time
from pathlib import Path
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 4000
DEFAULT_USERNAME = "dummy"
DEFAULT_PASSWORD = "helloworld"
ENCODING = "utf-8"


class MudClient:
    def __init__(self, host: str, port: int, settle: float) -> None:
        self.host = host
        self.port = port
        self.settle = settle
        self.socket: socket.socket | None = None

    def connect(self) -> None:
        self.socket = socket.create_connection((self.host, self.port), timeout=10)
        self.socket.setblocking(False)

    def close(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def read_until_quiet(self, quiet_after: float | None = None) -> str:
        """Read text until no bytes arrive for `quiet_after` seconds."""
        if self.socket is None:
            raise RuntimeError("Not connected")
        quiet_after = self.settle if quiet_after is None else quiet_after
        chunks: list[bytes] = []
        deadline = time.monotonic() + max(quiet_after, 0.05)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            readable, _, _ = select.select([self.socket], [], [], remaining)
            if not readable:
                break
            data = self.socket.recv(65536)
            if not data:
                break
            chunks.append(data)
            deadline = time.monotonic() + max(quiet_after, 0.05)
        return b"".join(chunks).decode(ENCODING, errors="replace")

    def read_until_any(self, markers: tuple[str, ...], timeout: float = 15.0) -> tuple[str, str]:
        """Read text until one of the case-insensitive markers is received."""
        if self.socket is None:
            raise RuntimeError("Not connected")
        chunks: list[bytes] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = deadline - time.monotonic()
            readable, _, _ = select.select([self.socket], [], [], remaining)
            if not readable:
                break
            data = self.socket.recv(65536)
            if not data:
                break
            chunks.append(data)
            text = b"".join(chunks).decode(ENCODING, errors="replace")
            lowered = text.lower()
            for marker in markers:
                if marker.lower() in lowered:
                    return text, marker
        raise TimeoutError(f"Timed out waiting for one of: {', '.join(markers)}")

    def send(self, command: str) -> str:
        if self.socket is None:
            raise RuntimeError("Not connected")
        self.socket.sendall((command.rstrip("\r\n") + "\n").encode(ENCODING))
        return self.read_until_quiet()

    def login(self, username: str, password: str) -> str:
        transcript, _ = self.read_until_any(("By what name do you wish to be known?",))
        response, marker = self.send_and_wait(
            username, ("Password:", "Did I get that right")
        )
        transcript += response
        if marker.lower().startswith("did i get that right"):
            response, _ = self.send_and_wait("yes", ("Password:",))
            transcript += response
        transcript += self.send(password)
        return transcript

    def send_and_wait(self, command: str, markers: tuple[str, ...]) -> tuple[str, str]:
        if self.socket is None:
            raise RuntimeError("Not connected")
        self.socket.sendall((command.rstrip("\r\n") + "\n").encode(ENCODING))
        return self.read_until_any(markers)


def get_commands(args: argparse.Namespace) -> list[str]:
    commands = list(args.command or [])
    if args.commands_file:
        lines = Path(args.commands_file).read_text(encoding=ENCODING).splitlines()
        commands.extend(line for line in lines if line.strip() and not line.lstrip().startswith("#"))
    return commands


def print_output(text: str) -> None:
    if text:
        print(text, end="" if text.endswith("\n") else "\n")


def interactive(client: MudClient) -> None:
    while True:
        try:
            command = input("mud> ")
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if command.strip().lower() in {"/quit", "/exit"}:
            return
        if command.strip():
            print_output(client.send(command))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Log in to a text MUD and send commands.")
    parser.add_argument("--host", default=os.getenv("MUD_HOST", DEFAULT_HOST))
    parser.add_argument("--port", type=int, default=int(os.getenv("MUD_PORT", DEFAULT_PORT)))
    parser.add_argument("--username", default=os.getenv("MUD_USERNAME", DEFAULT_USERNAME))
    parser.add_argument("--password", default=os.getenv("MUD_PASSWORD", DEFAULT_PASSWORD))
    parser.add_argument("--settle", type=float, default=0.35, metavar="SECONDS",
                        help="silence period that marks the end of a response (default: 0.35)")
    parser.add_argument("--command", action="append", help="MUD command to execute; may be repeated")
    parser.add_argument("--commands-file", help="text file containing one command per line")
    parser.add_argument("--interactive", action="store_true", help="enter an interactive prompt after login")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    commands = get_commands(args)
    if not commands and not args.interactive:
        args.interactive = True

    client = MudClient(args.host, args.port, args.settle)
    try:
        client.connect()
        print_output(client.login(args.username, args.password))
        for command in commands:
            print(f"> {command}")
            print_output(client.send(command))
        if args.interactive:
            interactive(client)
    except (OSError, RuntimeError) as error:
        print(f"MUD connection failed: {error}", file=sys.stderr)
        return 1
    finally:
        client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
