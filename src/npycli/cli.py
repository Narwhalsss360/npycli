from __future__ import annotations

from collections.abc import Callable
from shlex import split
from typing import TYPE_CHECKING, Any, Self

from .command import Command
from .errors import CLIError, CommandDoesNotExistError, EmptyEntriesError
from .parameters import CommandParameterType

if TYPE_CHECKING:
    from .middleware import (
        CommandAddedResult,
        ErrorResult,
        ExecutorResult,
        Middleware,
        PrompterResult,
        ReturnValueResult,
    )


class CLI:
    def __init__(
        self,
        title: str | None = None,
        prompt_marker: str | None = None,
        kwarg_prefix: str | None = None,
        parsers: dict[CommandParameterType, Callable[[str], Any]] | None = None,
        env: dict[Any, Any] | None = None,
        retval_handler: Callable[[Command, Any], Any] | None = None,
        error_handler: Callable[[Command, Exception], Any] | None = None,
    ) -> None:
        self.title: str = title or "CLI"
        self.prompt_marker: str = prompt_marker or ">"
        self.kwarg_prefix: str = kwarg_prefix or "--"
        self.parsers: dict[CommandParameterType, Callable[[str], Any]] = parsers or {}
        self.env: dict[Any, Any] = env or {}
        self._retval_handler: Callable[[Command, Any], Any] | None = retval_handler
        self._error_handler: Callable[[Command, Exception], Any] | None = error_handler
        self._commands: list[Command] = []
        self._middlewares: list[Middleware] = []

    @property
    def middlewares(self) -> list[Middleware]:
        return [mid for mid in self._middlewares]

    def use[T: Middleware](self, middleware: type[T]) -> Self:
        self._middlewares.append(middleware.on_use(self))
        return self

    @property
    def commands(self) -> list[Command]:
        """
        Get commands current added to this CLI.
        :return: commands
        """

        return self._commands

    @property
    def prompt_entry_marker(self) -> str:
        """
        Get the prompt entry marker for this CLI
        :return: *title* *prompt marker*
        """

        return f"{self.title}{self.prompt_marker}"

    def get_command(self, name: str) -> Command | None:
        """
        Get the command with the specified name. If it does not exist, `None` is returned.
        :param name: Name of command.
        :return: `Command` that matches `name`
        """

        return next(filter(lambda cmd: name in cmd.names, self.commands), None)

    def add_command(self, command: Command) -> None:
        """
        Append a `Command` to the list of commands on this CLI.
        :param command: `Command` to add.
        :return: `None`
        """

        last_flagged_result: CommandAddedResult | None = None
        last_result: CommandAddedResult | None = None
        for middleware in self._middlewares:
            result: CommandAddedResult = middleware.command_added(
                command, last_result, last_flagged_result
            )
            last_result = result
            if result.inhibit:
                last_flagged_result = result

        if last_flagged_result is None:
            self._commands.append(command)

    def cmd[**P, R](
        self,
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Curry function that creates a decorator that creates a `Command` from the function.
        :param name: Name of `Command`
        :param names: Names and aliases of `Command`. *Cannot be used with `name`*
        :param help: Help string
        :return: Decorator
        """

        def decorator(function: Callable[P, R]) -> Callable[P, R]:
            self.add_command(
                Command.create(
                    function=function,
                    name=name,
                    names=names,
                    help=help,
                    kwarg_prefix=self.kwarg_prefix,
                )
            )
            return function

        return decorator

    def retvals(
        self,
    ) -> Callable[[Callable[[Command, Any], None]], Callable[..., Any | None]]:
        """
        Curry function that creates a decorator to specify a return value handler function.
        :return: Decorator
        """

        def decorator(
            function: Callable[[Command, Any], None],
        ) -> Callable[[Command, Any], None]:
            self._retval_handler = function
            return function

        return decorator

    def errors(
        self,
    ) -> Callable[[Callable[[Command, Exception], None]], Callable[..., Any]]:
        """
        Curry function that creates a decorator to specify an error handler function.
        :return: Decorator
        """

        def decorator(
            function: Callable[[Command, Exception], None],
        ) -> Callable[[Command, Exception], None]:
            self._error_handler = function
            return function

        return decorator

    def exec(self, entries: list[str]) -> Any:
        """
        Execute a command from specified `entries`.
        :param entries: Command name and arguments.
        :return: Command function return value
        """

        if not entries:
            raise EmptyEntriesError("Nothing was entered.", cli=self)

        name: str = entries.pop(0)
        if (command := self.get_command(name)) is None:
            raise CommandDoesNotExistError(f"Command {name} does not exist.", cli=self)

        try:
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

            last_flagged_executor_result: ExecutorResult | None = None
            for middleware in self.middlewares:
                executor_result: ExecutorResult = middleware.executor(
                    command, last_flagged_executor_result
                )
                if executor_result.executor is not None:
                    last_flagged_executor_result = executor_result
                    executor = executor_result.executor

            command, retval = executor(command, entries, self.parsers)

            if self._retval_handler is not None:
                retval = self._retval_handler(command, retval)
        except CLIError as cli_error:
            last_error_result: ErrorResult | None = None
            for middleware in self._middlewares:
                error_result: ErrorResult = middleware.error(
                    command, cli_error, last_error_result
                )
                last_error_result = error_result

            if self._error_handler is None:
                cli_error.cli = self
                raise

            retval = self._error_handler(command, cli_error)
        except Exception as error:
            last_error_result: ErrorResult | None = None
            for middleware in self._middlewares:
                error_result: ErrorResult = middleware.error(
                    command, error, last_error_result
                )
                last_error_result = error_result

            if self._error_handler is None:
                raise CLIError(
                    f"An exception was raised running {command.name}: {error}",
                    cli=self,
                    command=command,
                ) from error
            retval = self._error_handler(command, error)

        last_return_value_result: ReturnValueResult | None = None
        for middleware in self._middlewares:
            return_value_result: ReturnValueResult = middleware.return_value(
                command, retval, last_return_value_result
            )
            last_return_value_result = return_value_result

        return retval

    def prompt(self) -> Any:
        """
        Prompt the user for entries to `exec` on this CLI.
        :return: Command function return value
        """

        prompter: Callable[[str], str] = lambda s: input(s)
        last_flagged_result: PrompterResult | None = None
        for middleware in self._middlewares:
            result: PrompterResult = middleware.prompter(last_flagged_result)
            if result.prompter is not None:
                last_flagged_result = result

        if last_flagged_result is not None and last_flagged_result.prompter is not None:
            prompter = last_flagged_result.prompter

        return self.exec(split(prompter(self.prompt_entry_marker)))


__all__ = ["CLI"]
