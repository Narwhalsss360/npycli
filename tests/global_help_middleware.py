from __future__ import annotations

from collections.abc import Callable
from typing import Any, override

import better_help as other_program

from npycli.cli import CLI
from npycli.command import Command
from npycli.errors import MiddlewareError
from npycli.middleware import ExecutorResult, Middleware
from npycli.parameters import (
    CommandParameterType,
    ParameterKind,
)


def create_global_help_middleware(
    help_cmd_name: str = "help",
    global_help_flag: str = "help",
    use_positional_count: int | None = None,
) -> type[Middleware]:
    class GlobalHelpMiddleware(Middleware):
        def __init__(self, cli: CLI, help_cmd: Command) -> None:
            super().__init__(cli)
            self._help_cmd: Command = help_cmd
            self._help_positionals_count: int = (
                sum(
                    1
                    for parameter in self._help_cmd.parameters
                    if parameter.kind
                    in (
                        ParameterKind.POSITIONAL_ONLY,
                        ParameterKind.POSITIONAL_OR_KEYWORD,
                    )
                )
                if use_positional_count is None
                else use_positional_count
            )
            if self._help_positionals_count < 0:
                raise ValueError("Cannot use a negative amount of positionals")

            self._help_bool_flag_names: tuple[str, ...] = tuple(
                parameter.name
                for parameter in self._help_cmd.parameters
                if parameter.kind
                in (ParameterKind.POSITIONAL_OR_KEYWORD, ParameterKind.KEYWORD_ONLY)
            )

            self._help_cmd.add_detail(f"To get help another way, enter in the following format: `<command-name> ... {self.cli.kwarg_prefix}{global_help_flag}` and all positional arguments and flags will get forwarded to the help command (the {self.cli.kwarg_prefix}{global_help_flag} global help flag need not be at the end, in fact anywhere except first.)")

        @classmethod
        @override
        def on_use(cls, cli: CLI) -> GlobalHelpMiddleware:
            for middleware in cli.middlewares:
                if isinstance(middleware, GlobalHelpMiddleware):
                    raise MiddlewareError(
                        f"{GlobalHelpMiddleware} is already registered for the cli.",
                        middleware=middleware,
                    )

            if (help_cmd := cli.get_command(help_cmd_name)) is None:
                raise MiddlewareError(
                    f"The help command '{help_cmd_name}' does not exist.",
                    middleware=None,
                )

            if any(
                global_help_flag in parameter.names
                for command in cli.commands
                for parameter in command.parameters
            ):
                raise MiddlewareError(
                    f"Cannot use gloval help flag '{global_help_flag}' since it is used by one of the command",
                    middleware=None,
                )

            return GlobalHelpMiddleware(cli, help_cmd)

        def _help_cmd_entries_result(
            self, command_entered: Command, entries: list[str]
        ) -> tuple[bool, list[str]]:
            has_help_flag: bool = False
            help_positionals: list[str] = [command_entered.name]
            bool_flags: list[str] = []
            for entry in entries:
                if entry == self.cli.kwarg_prefix:
                    return False, []

                if f"{self.cli.kwarg_prefix}{global_help_flag}" == entry:
                    has_help_flag = True
                    continue

                if entry.startswith(self.cli.kwarg_prefix):
                    no_prefix: str = entry[len(self.cli.kwarg_prefix) :]
                    if no_prefix in self._help_bool_flag_names:
                        bool_flags.append(entry)
                elif len(help_positionals) != self._help_positionals_count:
                    help_positionals.append(entry)

            return has_help_flag, [*help_positionals, *bool_flags]

        @override
        def executor(
            self, command: Command, last_flagged_result: ExecutorResult | None = None
        ) -> ExecutorResult:
            executor: Callable[
                [
                    Command,
                    list[str],
                    dict[CommandParameterType, Callable[[str], Any]] | None,
                ],
                tuple[Command, Any],
            ] = lambda cmd, entries, parsers: (
                cmd,
                Command.exec_with(cmd, entries, parsers),
            )

            if last_flagged_result and last_flagged_result.executor:
                executor = last_flagged_result.executor

            def this_executor(
                command: Command,
                entries: list[str],
                parsers: dict[CommandParameterType, Callable[[str], Any]] | None = None,
            ) -> tuple[Command, Any]:
                has_help_flag, help_entries = self._help_cmd_entries_result(
                    command, entries
                )
                if has_help_flag:
                    return executor(self._help_cmd, help_entries, self.cli.parsers)
                return executor(command, entries, parsers)

            return ExecutorResult(self, this_executor)

    return GlobalHelpMiddleware


def main() -> None:
    other_program.cli.use(create_global_help_middleware())
    other_program.main()


if __name__ == "__main__":
    main()
