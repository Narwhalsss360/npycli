from __future__ import annotations

from collections.abc import Callable, Sequence
from shlex import split
from typing import Any, Self

from .command import Command
from .errors import CLIError, CommandDoesNotExistError, EmptyEntriesError
from .middleware import (
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
    CommandForMiddlewareHandlerInfo,
    ErrorMiddlewareHandler,
    ErrorMiddlewareHandlerInfo,
    ExecutorMiddlewareHandler,
    ExecutorMiddlewareHandlerInfo,
    ExecutorMiddlewareResult,
    MiddlewareContext,
    PromptMiddlewareHandler,
    PromptMiddlewareHandlerInfo,
    ReturnValueMiddlewareHandler,
    ReturnValueMiddlewareHandlerInfo,
    SplitMiddlewareHandler,
    SplitMiddlewareHandlerInfo,
)
from .parameters import Parsers

type ReturnValueHandler = Callable[[Command, Any], Any]

type ErrorHandler = Callable[[Command, Exception], Any]


class RaiseExpectionSentinelType:
    __slots__ = ()

    def __repr__(self) -> str:
        return "<Raise Exception Sentinel>"

    def __setattr__(self, name: str, value: Any):
        raise AttributeError("This sentinel instance is immutable.")

    def __delattr__(self, name: str):
        raise AttributeError("This sentinel instances is immutable.")

    def __copy__(self):
        return self

    def __deepcopy__(self, memo: Any):
        return self


class CLI:
    RAISE: RaiseExpectionSentinelType = RaiseExpectionSentinelType()

    class MiddlewareManager:
        class Register:
            def __init__(self, middleware_manager: CLI.MiddlewareManager) -> None:
                self._middlware_manager: CLI.MiddlewareManager = middleware_manager

            def prompt(
                self,
            ) -> Callable[[PromptMiddlewareHandler], PromptMiddlewareHandler]:
                def decorator(
                    prompter: PromptMiddlewareHandler,
                ) -> PromptMiddlewareHandler:
                    self._middlware_manager.set_prompt_middleware(prompter)
                    return prompter

                return decorator

            def split(
                self,
            ) -> Callable[[SplitMiddlewareHandler], SplitMiddlewareHandler]:
                def decorator(
                    splitter: SplitMiddlewareHandler,
                ) -> SplitMiddlewareHandler:
                    self._middlware_manager.set_split_middleware(splitter)
                    return splitter

                return decorator

            def command_execution_info(
                self, wrapping: bool = True
            ) -> Callable[
                [CommandExecutionInfoMiddlewareHandler],
                CommandExecutionInfoMiddlewareHandler,
            ]:
                def decorator(
                    command_execution_info: CommandExecutionInfoMiddlewareHandler,
                ) -> CommandExecutionInfoMiddlewareHandler:
                    if wrapping:
                        self._middlware_manager.wrap_command_execution_info_middleware(
                            command_execution_info
                        )
                    else:
                        self._middlware_manager.set_command_execution_info_middleware(
                            command_execution_info
                        )
                    return command_execution_info

                return decorator

            def executor(
                self, wrapping: bool = True
            ) -> Callable[[ExecutorMiddlewareHandler], ExecutorMiddlewareHandler]:
                def decorator(
                    executor: ExecutorMiddlewareHandler,
                ) -> ExecutorMiddlewareHandler:
                    if wrapping:
                        self._middlware_manager.wrap_executor_middleware(executor)
                    else:
                        self._middlware_manager.set_executor_middleware(executor)
                    return executor

                return decorator

            def error(
                self, wrapping: bool = True
            ) -> Callable[[ErrorMiddlewareHandler], ErrorMiddlewareHandler]:
                def decorator(
                    error_handler: ErrorMiddlewareHandler,
                ) -> ErrorMiddlewareHandler:
                    if wrapping:
                        self._middlware_manager.wrap_error_middleware(error_handler)
                    else:
                        self._middlware_manager.set_error_middleware(error_handler)
                    return error_handler

                return decorator

            def return_value(
                self, wrapping: bool = True
            ) -> Callable[[ReturnValueMiddlewareHandler], ReturnValueMiddlewareHandler]:
                def decorator(
                    return_value: ReturnValueMiddlewareHandler,
                ) -> ReturnValueMiddlewareHandler:
                    if wrapping:
                        self._middlware_manager.wrap_return_value_middleware(
                            return_value
                        )
                    else:
                        self._middlware_manager.set_return_value_middleware(
                            return_value
                        )
                    return return_value

                return decorator

        def __init__(self, cli: CLI) -> None:
            self._cli: CLI = cli
            self._prompt_middleware_handler_info: PromptMiddlewareHandlerInfo = (
                PromptMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.default_prompter, MiddlewareContext(self.cli)
                )
            )
            self._split_middleware_handler_info: SplitMiddlewareHandlerInfo = (
                SplitMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.default_splitter, MiddlewareContext(self.cli)
                )
            )
            self._command_execution_info_handler_handler_info: CommandForMiddlewareHandlerInfo = CommandForMiddlewareHandlerInfo(
                CLI.MiddlewareManager.default_command_execution_info,
                MiddlewareContext(self.cli),
            )
            self._executor_middleware_handler_info: ExecutorMiddlewareHandlerInfo = (
                ExecutorMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.default_executor, MiddlewareContext(self.cli)
                )
            )
            self._error_middleware_handler_info: ErrorMiddlewareHandlerInfo = (
                ErrorMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.default_error_handler,
                    MiddlewareContext(self.cli),
                )
            )
            self._return_value_middleware_handler_info: ReturnValueMiddlewareHandlerInfo = ReturnValueMiddlewareHandlerInfo(
                CLI.MiddlewareManager.default_return_value_handler,
                MiddlewareContext(self.cli),
            )

        @property
        def cli(self) -> CLI:
            return self._cli

        @property
        def register(self) -> CLI.MiddlewareManager.Register:
            return CLI.MiddlewareManager.Register(self)

        @staticmethod
        def default_prompter(_: MiddlewareContext, prompt: str) -> str:
            return input(prompt)

        def set_prompt_middleware(self, prompter: PromptMiddlewareHandler) -> Self:
            self._prompt_middleware_handler_info.handler = prompter
            return self

        def prompt(self, prompt: str) -> str:
            return self._prompt_middleware_handler_info.handler(
                self._prompt_middleware_handler_info.context, prompt
            )

        @staticmethod
        def default_splitter(_: MiddlewareContext, entry: str) -> list[str]:
            return split(entry)

        def set_split_middleware(self, splitter: SplitMiddlewareHandler) -> Self:
            self._split_middleware_handler_info.handler = splitter
            return self

        def split(self, s: str) -> Sequence[str]:
            return self._split_middleware_handler_info.handler(
                self._split_middleware_handler_info.context, s
            )

        @staticmethod
        def default_command_execution_info(
            context: MiddlewareContext, entries: Sequence[str]
        ) -> CommandExecutionInfoMiddlewareResult:
            return CommandExecutionInfoMiddlewareResult(
                context.cli.get_command(entries[0]) if entries else None, entries[1:]
            )

        def set_command_execution_info_middleware(
            self, command_execution_info: CommandExecutionInfoMiddlewareHandler
        ) -> Self:
            self._command_execution_info_handler_handler_info.handler = (
                command_execution_info
            )
            return self

        def wrap_command_execution_info_middleware(
            self, command_execution_info: CommandExecutionInfoMiddlewareHandler
        ) -> Self:
            if (
                self._command_execution_info_handler_handler_info.handler
                is self.default_command_execution_info
            ):
                return self.set_command_execution_info_middleware(
                    command_execution_info
                )

            def wrapper(
                context: MiddlewareContext, entries: Sequence[str]
            ) -> CommandExecutionInfoMiddlewareResult:
                previous_result: CommandExecutionInfoMiddlewareResult = (
                    self._command_execution_info_handler_handler_info.handler(
                        context, entries
                    )
                )
                return command_execution_info(
                    MiddlewareContext(
                        self.cli,
                        context.base_result
                        if context.base_result is not context.DNE
                        else previous_result,
                        previous_result,
                    ),
                    entries,
                )

            self._command_execution_info_handler_handler_info.handler = wrapper
            return self

        def command_execution_info(
            self, entries: Sequence[str]
        ) -> CommandExecutionInfoMiddlewareResult:
            return self._command_execution_info_handler_handler_info.handler(
                self._command_execution_info_handler_handler_info.context, entries
            )

        @staticmethod
        def default_executor(
            _: MiddlewareContext,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers,
        ) -> ExecutorMiddlewareResult:
            return ExecutorMiddlewareResult(
                command, command.exec_with(entries, parsers)
            )

        @staticmethod
        def executor_wrapper_base(
            _: MiddlewareContext,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers,
        ) -> ExecutorMiddlewareResult:
            return ExecutorMiddlewareResult(
                command, command.exec_with(entries, parsers)
            )

        def set_executor_middleware(self, executor: ExecutorMiddlewareHandler) -> Self:
            self._executor_middleware_handler_info.handler = executor
            return self

        def wrap_executor_middleware(self, executor: ExecutorMiddlewareHandler) -> Self:
            if self._executor_middleware_handler_info.handler is self.default_executor:
                return self.set_executor_middleware(executor)

            def wrapper(
                context: MiddlewareContext,
                command: Command,
                entries: Sequence[str],
                parsers: Parsers,
            ) -> ExecutorMiddlewareResult:
                previous_result: ExecutorMiddlewareResult = (
                    self._executor_middleware_handler_info.handler(
                        context, command, entries, parsers
                    )
                )
                return executor(
                    MiddlewareContext(
                        self.cli,
                        context.base_result
                        if context.base_result is not context.DNE
                        else previous_result,
                        previous_result,
                    ),
                    previous_result.command_executed,
                    entries,
                    parsers,
                )

            self._executor_middleware_handler_info.handler = wrapper
            return self

        def executor(
            self, command: Command, entries: Sequence[str], parsers: Parsers
        ) -> ExecutorMiddlewareResult:
            return self._executor_middleware_handler_info.handler(
                self._executor_middleware_handler_info.context,
                command,
                entries,
                parsers,
            )

        @staticmethod
        def default_error_handler(
            _: MiddlewareContext, command: Command, error: Exception
        ) -> Any:
            return CLI.RAISE

        def set_error_middleware(self, error_handler: ErrorMiddlewareHandler) -> Self:
            self._error_middleware_handler_info.handler = error_handler
            return self

        def wrap_error_middleware(self, error_handler: ErrorMiddlewareHandler) -> Self:
            if (
                self._error_middleware_handler_info.handler
                is self.default_error_handler
            ):
                return self.set_error_middleware(error_handler)

            def wrapper(
                context: MiddlewareContext, command: Command, error: Exception
            ) -> Any:
                previous_result: ErrorMiddlewareHandler = (
                    self._error_middleware_handler_info.handler(context, command, error)
                )
                return error_handler(
                    MiddlewareContext(
                        self.cli,
                        context.base_result
                        if context.base_result is not context.DNE
                        else previous_result,
                        previous_result,
                    ),
                    command,
                    error,
                )

            self._error_middleware_handler_info.handler = wrapper
            return self

        def error(self, command: Command, error: Exception) -> Any:
            return self._error_middleware_handler_info.handler(
                self._error_middleware_handler_info.context, command, error
            )

        @staticmethod
        def default_return_value_handler(
            _: MiddlewareContext, command: Command, return_value: Any
        ) -> Any:
            return return_value

        def set_return_value_middleware(
            self, return_value_handler: ReturnValueMiddlewareHandler
        ) -> Self:
            self._return_value_middleware_handler_info.handler = return_value_handler
            return self

        def wrap_return_value_middleware(
            self, return_value_handler: ReturnValueMiddlewareHandler
        ) -> Self:
            if (
                self._return_value_middleware_handler_info.handler
                is self.default_return_value_handler
            ):
                return self.set_return_value_middleware(return_value_handler)

            def wrapper(
                context: MiddlewareContext, command: Command, return_value: Any
            ) -> Any:
                previous_result: Any = (
                    self._return_value_middleware_handler_info.handler(
                        context, command, return_value
                    ),
                )
                return return_value_handler(
                    MiddlewareContext(
                        self.cli,
                        context.base_result is context.base_result is not context.DNE,
                        previous_result,
                    ),
                    command,
                    return_value,
                )

            self._return_value_middleware_handler_info.handler = wrapper
            return self

        def return_value(self, command: Command, return_value: Any) -> Any:
            return self._return_value_middleware_handler_info.handler(
                self._return_value_middleware_handler_info.context,
                command,
                return_value,
            )

    def __init__(
        self,
        title: str | None = None,
        prompt_marker: str | None = None,
        kwarg_prefix: str | None = None,
        parsers: Parsers | None = None,
        env: dict[Any, Any] | None = None,
        retval_handler: ReturnValueHandler | None = None,
        error_handler: ErrorHandler | None = None,
    ) -> None:
        self.title: str = title or "CLI"
        self.prompt_marker: str = prompt_marker or ">"
        self.kwarg_prefix: str = kwarg_prefix or "--"
        self.parsers: Parsers = parsers or {}
        self.env: dict[Any, Any] = env or {}
        self._commands: list[Command] = []
        self._middleware_manager: CLI.MiddlewareManager = CLI.MiddlewareManager(self)
        if retval_handler is not None:
            self.retvals()(retval_handler)
        if error_handler is not None:
            self.errors()(error_handler)

    @property
    def middlewares(self) -> MiddlewareManager:
        return self._middleware_manager

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

        try:
            return next(filter(lambda cmd: name in cmd.names, self.commands))
        except StopIteration:
            return None

    def add_command(self, command: Command) -> None:
        """
        Append a `Command` to the list of commands on this CLI.
        :param command: `Command` to add.
        :return: `None`
        """

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
            def wrapper(
                _: MiddlewareContext, command: Command, return_value: Any
            ) -> Any:
                return function(command, return_value)

            self.middlewares.set_return_value_middleware(wrapper)
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
            def wrapper(
                _: MiddlewareContext, command: Command, return_value: Any
            ) -> Any:
                return function(command, return_value)

            self.middlewares.set_error_middleware(wrapper)
            return function

        return decorator

    def command_execution_info(
        self, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        return self.middlewares.command_execution_info(entries)

    def exec(self, entries: Sequence[str]) -> Any:
        """
        Execute a command from specified `entries`.
        :param entries: Command name and arguments.
        :return: Command function return value
        """

        if not entries:
            command_execution_info: CommandExecutionInfoMiddlewareResult = (
                self.command_execution_info(entries)
            )
            if (command := command_execution_info.command) is None:
                raise EmptyEntriesError("Nothing was entered.", cli=self)
        else:
            command_execution_info: CommandExecutionInfoMiddlewareResult = (
                self.command_execution_info(entries)
            )
            if (command := command_execution_info.command) is None:
                raise CommandDoesNotExistError(
                    f"Command {entries[0]} does not exist.", cli=self
                )

        try:
            command, return_value = self._middleware_manager.executor(
                command, command_execution_info.arg_entries, self.parsers
            )
            return_value = self._middleware_manager.return_value(command, return_value)
        except CLIError as cli_error:
            if (
                return_value := self.middlewares.error(command, cli_error)
            ) is CLI.RAISE:
                raise
        except Exception as error:
            if (return_value := self.middlewares.error(command, error)) is CLI.RAISE:
                raise CLIError(
                    f"An exception was raised running {command.name}: {error}",
                    cli=self,
                    command=command,
                ) from error

        return return_value

    def prompt(self) -> Any:
        """
        Prompt the user for entries to `exec` on this CLI.
        :return: Command function return value
        """

        return self.exec(
            self._middleware_manager.split(
                self._middleware_manager.prompt(self.prompt_entry_marker)
            )
        )


__all__ = ["CLI"]
