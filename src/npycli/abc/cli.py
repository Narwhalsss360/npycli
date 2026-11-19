from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import to_thread
from collections.abc import Callable, Generator, Sequence
from shlex import split
from typing import Any, Self

from ..errors import CLIError, CommandDoesNotExistError, EmptyEntriesError
from ..middleware import (
    CommandExecutionInfoHandlerInfo,
    CommandExecutionInfoMiddlewareHandler,
    CommandExecutionInfoMiddlewareResult,
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
    sync,
    wrap_sync,
)
from ..parsing import CommandParameterParser, Parsers
from .command import INVALID_COMMAND, Command

type ReturnValueHandler = Callable[[Command, Any], Any]

type ErrorHandler = Callable[[Command, Exception], Any]


class RaiseExpectionSentinelType:
    """A type that represents a sentinel type that an error middleware handler shall return to convey that an error is, in fact, unhandled
    This creates an instance which is immutable/uncopyable to represent the sentinel, though, each singleton is indepedent of each other.
    """

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


class CLI(ABC):
    """The CLI (Command-line Interface) abstract-base class.
    This class has a list of commands which may be executed.

    This abstract base class has synchronous and asynchronous implementations.

    Title: The 'title' attribute is used from prompting
    Parsing: The parser (CommandParameterParser) may be specified in the constructor. This is a mutable attribute of CLI.

    An asynchronous/synchronous CLI may be discriminated by checking the is_async property.

    The following defines how commands of this CLI are executed.
    - Command switching is done by the command execution info middleware
    - Command execution is done by the executor middleware
    - (a)sync_exec exceptions may be handled by an error middleware. If the error middleware return the CLI.RAISE sentinel, the exceptions gets raised on the frame of the (a)sync_exec function.
    - (a)sync_exec return value depends on the return value middleware

    The cli may also prompt the user. This is defined by:
    - the (a)sync_prompt function
    - The prompt middleware
    - The split middlware
    - The return value of (a)sync_prompt is the return value of (a)sync_exec

    Note: this abstract base class is awaitable, if not overriden, an exception is raised.

    Middlewares: Middleware handlers may be set or wrapped.
    - Setting handler: Setting a handler means that all previous handler, even if wrapped, get's overriden
    - Wrapping handler: Wrap an existing handler, the previous result would be stored in the MiddlewareContext argument
    - The 'middlewares' property returns a CLI.MiddlewareManager instance which may be used to register middlewares.

    Legacy retvals and errors decorator_factories exist, they are registered as a middleware, wrapped to match signature

    Subclass implementation expectations:
    The subclass is expected to implement the methods exec() and __call__(), by convention. This abstract-base class sets no constraints.
    Also, an __await__, if an asynchronous implementation.
    """

    RAISE: RaiseExpectionSentinelType = RaiseExpectionSentinelType()
    REPLACE: RaiseExpectionSentinelType = RaiseExpectionSentinelType()

    class MiddlewareManager:
        class Register:
            def __init__(self, middleware_manager: CLI.MiddlewareManager) -> None:
                self._middlware_manager: CLI.MiddlewareManager = middleware_manager

            def prompt[F: PromptMiddlewareHandler](
                self,
            ) -> Callable[[F], F]:
                def decorator(
                    prompter: F,
                ) -> F:
                    self._middlware_manager.set_prompt_middleware(prompter)
                    return prompter

                return decorator

            def split[F: SplitMiddlewareHandler](
                self,
            ) -> Callable[[F], F]:
                def decorator(
                    splitter: F,
                ) -> F:
                    self._middlware_manager.set_split_middleware(splitter)
                    return splitter

                return decorator

            def command_execution_info[F: CommandExecutionInfoMiddlewareHandler](
                self, wrapping: bool = True
            ) -> Callable[
                [F],
                F,
            ]:
                def decorator(
                    command_execution_info: F,
                ) -> F:
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

            def executor[F: ExecutorMiddlewareHandler](
                self, wrapping: bool = True
            ) -> Callable[[F], F]:
                def decorator(
                    executor: F,
                ) -> F:
                    if wrapping:
                        self._middlware_manager.wrap_executor_middleware(executor)
                    else:
                        self._middlware_manager.set_executor_middleware(executor)
                    return executor

                return decorator

            def error[F: ErrorMiddlewareHandler](
                self, wrapping: bool = True
            ) -> Callable[[F], F]:
                def decorator(
                    error_handler: F,
                ) -> F:
                    if wrapping:
                        self._middlware_manager.wrap_error_middleware(error_handler)
                    else:
                        self._middlware_manager.set_error_middleware(error_handler)
                    return error_handler

                return decorator

            def return_value[F: ReturnValueMiddlewareHandler](
                self, wrapping: bool = True
            ) -> Callable[[F], F]:
                def decorator(
                    return_value: F,
                ) -> F:
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
            if cli.is_async:
                self._use_async_defaults()
            else:
                self._use_sync_defaults()

        def _use_async_defaults(self) -> None:
            self._prompt_middleware_handler_info: PromptMiddlewareHandlerInfo = (
                PromptMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.async_default_prompter,
                    MiddlewareContext(self.cli),
                )
            )
            self._split_middleware_handler_info: SplitMiddlewareHandlerInfo = (
                SplitMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.async_default_splitter,
                    MiddlewareContext(self.cli),
                )
            )
            self._command_execution_info_handler_handler_info: CommandExecutionInfoHandlerInfo = CommandExecutionInfoHandlerInfo(
                CLI.MiddlewareManager.async_default_command_execution_info,
                MiddlewareContext(self.cli),
            )
            self._executor_middleware_handler_info: ExecutorMiddlewareHandlerInfo = (
                ExecutorMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.async_default_executor,
                    MiddlewareContext(self.cli),
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

        def _use_sync_defaults(self) -> None:
            self._prompt_middleware_handler_info: PromptMiddlewareHandlerInfo = (
                PromptMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.sync_default_prompter,
                    MiddlewareContext(self.cli),
                )
            )
            self._split_middleware_handler_info: SplitMiddlewareHandlerInfo = (
                SplitMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.sync_default_splitter,
                    MiddlewareContext(self.cli),
                )
            )
            self._command_execution_info_handler_handler_info: CommandExecutionInfoHandlerInfo = CommandExecutionInfoHandlerInfo(
                CLI.MiddlewareManager.sync_default_command_execution_info,
                MiddlewareContext(self.cli),
            )
            self._executor_middleware_handler_info: ExecutorMiddlewareHandlerInfo = (
                ExecutorMiddlewareHandlerInfo(
                    CLI.MiddlewareManager.sync_default_executor,
                    MiddlewareContext(self.cli),
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
        def is_async(self) -> bool:
            return self._cli.is_async

        @property
        def register(self) -> CLI.MiddlewareManager.Register:
            return CLI.MiddlewareManager.Register(self)

        @staticmethod
        def sync_default_prompter(_: MiddlewareContext, prompt: str) -> str:
            return input(prompt)

        @staticmethod
        async def async_default_prompter(_: MiddlewareContext, prompt: str) -> str:
            return await to_thread(input, prompt)

        def set_prompt_middleware(self, prompter: PromptMiddlewareHandler) -> Self:
            self._prompt_middleware_handler_info.handler = prompter
            return self

        def sync_prompt(self, prompt: str) -> str:
            return sync(
                self._prompt_middleware_handler_info.handler,
                self._prompt_middleware_handler_info.context,
                prompt,
            )

        async def async_prompt(self, prompt: str) -> str:
            return await wrap_sync(
                self._prompt_middleware_handler_info.handler,
                self._prompt_middleware_handler_info.context,
                prompt,
            )

        @staticmethod
        def sync_default_splitter(_: MiddlewareContext, entry: str) -> list[str]:
            return split(entry)

        @staticmethod
        async def async_default_splitter(
            context: MiddlewareContext, entry: str
        ) -> list[str]:
            return CLI.MiddlewareManager.sync_default_splitter(context, entry)

        def set_split_middleware(self, splitter: SplitMiddlewareHandler) -> Self:
            self._split_middleware_handler_info.handler = splitter
            return self

        def sync_split(self, s: str) -> Sequence[str]:
            return sync(
                self._split_middleware_handler_info.handler,
                self._split_middleware_handler_info.context,
                s,
            )

        async def async_split(self, s: str) -> Sequence[str]:
            return await wrap_sync(
                self._split_middleware_handler_info.handler,
                self._split_middleware_handler_info.context,
                s,
            )

        @staticmethod
        def sync_default_command_execution_info(
            context: MiddlewareContext, entries: Sequence[str]
        ) -> CommandExecutionInfoMiddlewareResult:
            return CommandExecutionInfoMiddlewareResult(
                context.cli.get_command(entries[0]) if entries else None, entries[1:]
            )

        @staticmethod
        async def async_default_command_execution_info(
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
            if self._command_execution_info_handler_handler_info.handler in (
                self.sync_default_command_execution_info,
                self.async_default_command_execution_info,
            ):
                return self.set_command_execution_info_middleware(
                    command_execution_info
                )

            wrapped: CommandExecutionInfoMiddlewareHandler = (
                self._command_execution_info_handler_handler_info.handler
            )

            if self.is_async:

                async def async_wrapper(
                    context: MiddlewareContext, entries: Sequence[str]
                ) -> CommandExecutionInfoMiddlewareResult:
                    previous_result: CommandExecutionInfoMiddlewareResult = (
                        await wrap_sync(
                            wrapped,
                            context,
                            entries,
                        )
                    )
                    return await wrap_sync(
                        command_execution_info,
                        MiddlewareContext(
                            self.cli,
                            context.base_result
                            if context.base_result is not context.DNE
                            else previous_result,
                            previous_result,
                        ),
                        entries,
                    )

                self._command_execution_info_handler_handler_info.handler = (
                    async_wrapper
                )
            else:

                def sync_wrapper(
                    context: MiddlewareContext, entries: Sequence[str]
                ) -> CommandExecutionInfoMiddlewareResult:
                    previous_result: CommandExecutionInfoMiddlewareResult = sync(
                        wrapped,
                        context,
                        entries,
                    )
                    return sync(
                        command_execution_info,
                        MiddlewareContext(
                            self.cli,
                            context.base_result
                            if context.base_result is not context.DNE
                            else previous_result,
                            previous_result,
                        ),
                        entries,
                    )

                self._command_execution_info_handler_handler_info.handler = sync_wrapper

            return self

        def sync_command_execution_info(
            self, entries: Sequence[str]
        ) -> CommandExecutionInfoMiddlewareResult:
            return sync(
                self._command_execution_info_handler_handler_info.handler,
                self._command_execution_info_handler_handler_info.context,
                entries,
            )

        async def async_command_execution_info(
            self, entries: Sequence[str]
        ) -> CommandExecutionInfoMiddlewareResult:
            return await wrap_sync(
                self._command_execution_info_handler_handler_info.handler,
                self._command_execution_info_handler_handler_info.context,
                entries,
            )

        @staticmethod
        def sync_default_executor(
            _: MiddlewareContext,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers | CommandParameterParser,
        ) -> ExecutorMiddlewareResult:
            return ExecutorMiddlewareResult(
                command, command.sync_exec_with(entries, parsers)
            )

        @staticmethod
        async def async_default_executor(
            _: MiddlewareContext,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers | CommandParameterParser,
        ) -> ExecutorMiddlewareResult:
            return ExecutorMiddlewareResult(
                command, await command.async_exec_with(entries, parsers)
            )

        def set_executor_middleware(self, executor: ExecutorMiddlewareHandler) -> Self:
            self._executor_middleware_handler_info.handler = executor
            return self

        def wrap_executor_middleware(self, executor: ExecutorMiddlewareHandler) -> Self:
            if self._executor_middleware_handler_info.handler in (
                self.sync_default_executor,
                self.async_default_executor,
            ):
                return self.set_executor_middleware(executor)

            wrapped: ExecutorMiddlewareHandler = (
                self._executor_middleware_handler_info.handler
            )

            if self.cli.is_async:

                async def async_wrapper(
                    context: MiddlewareContext,
                    command: Command,
                    entries: Sequence[str],
                    parsers: Parsers | CommandParameterParser,
                ) -> ExecutorMiddlewareResult:
                    previous_result: ExecutorMiddlewareResult = await wrap_sync(
                        wrapped,
                        context,
                        command,
                        entries,
                        parsers,
                    )
                    return await wrap_sync(
                        executor,
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

                self._executor_middleware_handler_info.handler = async_wrapper
            else:

                def sync_wrapper(
                    context: MiddlewareContext,
                    command: Command,
                    entries: Sequence[str],
                    parsers: Parsers | CommandParameterParser,
                ) -> ExecutorMiddlewareResult:
                    previous_result: ExecutorMiddlewareResult = sync(
                        wrapped,
                        context,
                        command,
                        entries,
                        parsers,
                    )
                    return sync(
                        executor,
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

                self._executor_middleware_handler_info.handler = sync_wrapper
            return self

        def sync_executor(
            self,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers | CommandParameterParser,
        ) -> ExecutorMiddlewareResult:
            return sync(
                self._executor_middleware_handler_info.handler,
                self._executor_middleware_handler_info.context,
                command,
                entries,
                parsers,
            )

        async def async_executor(
            self,
            command: Command,
            entries: Sequence[str],
            parsers: Parsers | CommandParameterParser,
        ) -> ExecutorMiddlewareResult:
            return await wrap_sync(
                self._executor_middleware_handler_info.handler,
                self._executor_middleware_handler_info.context,
                command,
                entries,
                parsers,
            )

        @staticmethod
        def default_error_handler(
            _: MiddlewareContext, command: Command | None, error: Exception
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

            wrapped: ErrorMiddlewareHandler = (
                self._error_middleware_handler_info.handler
            )

            if self.is_async:

                async def async_wrapper(
                    context: MiddlewareContext,
                    command: Command | None,
                    error: Exception,
                ) -> Any:
                    previous_result: ErrorMiddlewareHandler = await wrap_sync(
                        wrapped,
                        context,
                        command,
                        error,
                    )
                    return await wrap_sync(
                        error_handler,
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

                self._error_middleware_handler_info.handler = async_wrapper
            else:

                def sync_wrapper(
                    context: MiddlewareContext,
                    command: Command | None,
                    error: Exception,
                ) -> Any:
                    previous_result: ErrorMiddlewareHandler = sync(
                        wrapped,
                        context,
                        command,
                        error,
                    )
                    return sync(
                        error_handler,
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

                self._error_middleware_handler_info.handler = sync_wrapper
            return self

        def sync_error(self, command: Command | None, error: Exception) -> Any:
            return self._error_middleware_handler_info.handler(
                self._error_middleware_handler_info.context, command, error
            )

        async def async_error(self, command: Command | None, error: Exception) -> Any:
            return await wrap_sync(
                self._error_middleware_handler_info.handler,
                self._error_middleware_handler_info.context,
                command,
                error,
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

            wrapped: ReturnValueMiddlewareHandler = (
                self._return_value_middleware_handler_info.handler
            )

            if self.is_async:

                async def async_wrapper(
                    context: MiddlewareContext, command: Command, return_value: Any
                ) -> Any:
                    previous_result: Any = await wrap_sync(
                        wrapped,
                        context,
                        command,
                        return_value,
                    )
                    return await wrap_sync(
                        return_value_handler,
                        MiddlewareContext(
                            self.cli,
                            context.base_result
                            is context.base_result
                            is not context.DNE,
                            previous_result,
                        ),
                        command,
                        return_value,
                    )

                self._return_value_middleware_handler_info.handler = async_wrapper
            else:

                def sync_wrapper(
                    context: MiddlewareContext, command: Command, return_value: Any
                ) -> Any:
                    previous_result: Any = sync(
                        wrapped,
                        context,
                        command,
                        return_value,
                    )
                    return sync(
                        return_value_handler,
                        MiddlewareContext(
                            self.cli,
                            context.base_result
                            is context.base_result
                            is not context.DNE,
                            previous_result,
                        ),
                        command,
                        return_value,
                    )

                self._return_value_middleware_handler_info.handler = sync_wrapper
            return self

        def sync_return_value(self, command: Command, return_value: Any) -> Any:
            return self._return_value_middleware_handler_info.handler(
                self._return_value_middleware_handler_info.context,
                command,
                return_value,
            )

        async def async_return_value(self, command: Command, return_value: Any) -> Any:
            return await wrap_sync(
                self._return_value_middleware_handler_info.handler,
                self._return_value_middleware_handler_info.context,
                command,
                return_value,
            )

    def __init__(
        self,
        title: str | None = None,
        prompt_marker: str | None = None,
        parser: CommandParameterParser | None = None,
        retval_handler: ReturnValueHandler | None = None,
        error_handler: ErrorHandler | None = None,
    ) -> None:
        self.title: str = title or "CLI"
        self.prompt_marker: str = prompt_marker or ">"
        self._parser: CommandParameterParser = parser or CommandParameterParser()
        self._commands: list[Command] = []
        self._middleware_manager: CLI.MiddlewareManager = CLI.MiddlewareManager(self)
        if retval_handler is not None:
            self.retvals()(retval_handler)
        if error_handler is not None:
            self.errors()(error_handler)

    @property
    def parser(self) -> CommandParameterParser:
        """Get the parser of this CLI"""

        return self._parser

    @parser.setter
    def parser(self, value: CommandParameterParser) -> None:
        """Set the parser. Also sets all command of CLI default_parser to this value."""

        self._parser = value
        for command in self._commands:
            command.with_default_parser(self._parser)

    @property
    @abstractmethod
    def is_async(self) -> bool:
        """Whether this CLI has asynchronous implementations."""

        ...

    @property
    def middlewares(self) -> MiddlewareManager:
        """Get the middleware manager of this CLI."""

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

    @property
    def has_invoked_callbacks(self) -> bool:
        """Whether all commands of this CLI has invoked all callbacks (hooks)"""

        return all(command.has_invoked_callbacks for command in self._commands)

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

        self._commands.append(command.with_default_parser(self._parser))

    @abstractmethod
    def cmd[F: Callable[..., Any]](
        self,
        name: str | None = None,
        names: tuple[str, ...] | None = None,
        help: str | None = None,
    ) -> Callable[[F], F]:
        """Decorator factory that creates a command out of the function and add the command to this CLI."""
        ...

    def retvals[F: ReturnValueHandler](
        self,
    ) -> Callable[[F], F]:
        """
        Curry function that creates a decorator to specify a return value handler function.
        :return: Decorator
        """

        def decorator(
            function: F,
        ) -> F:
            if self.is_async:

                async def wrapper(
                    _: MiddlewareContext, command: Command, return_value: Any
                ) -> Any:
                    return await wrap_sync(function, command, return_value)

                self.middlewares.set_return_value_middleware(wrapper)
            else:
                self.middlewares.set_return_value_middleware(
                    lambda _, command, return_value: function(command, return_value)
                )
            return function

        return decorator

    def errors[F: ErrorHandler](
        self,
    ) -> Callable[[F], F]:
        """
        Curry function that creates a decorator to specify an error handler function.
        :return: Decorator
        """

        def decorator(
            function: F,
        ) -> F:

            if self.is_async:

                async def wrapper(
                    _: MiddlewareContext, command: Command | None, error: Exception
                ) -> Any:
                    return wrap_sync(function, INVALID_COMMAND, error)

                self.middlewares.set_error_middleware(wrapper)
            else:
                self.middlewares.set_error_middleware(
                    lambda _, command, error: function(INVALID_COMMAND, error)
                )
            return function

        return decorator

    def sync_command_execution_info(
        self, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        """Get the command execution info through registered middlewares."""

        return self.middlewares.sync_command_execution_info(entries)

    async def async_command_execution_info(
        self, entries: Sequence[str]
    ) -> CommandExecutionInfoMiddlewareResult:
        """Get the command execution info through registered middlewares (asynchronously)."""

        return await self.middlewares.async_command_execution_info(entries)

    def sync_exec(self, entries: Sequence[str]) -> Any:
        """
        Execute a command from specified `entries`, synchronously.
        :param entries: Command name (default middleware behavior) and arguments.
        :return: Command function return value
        """

        command: Command | None = None
        try:
            if not entries:
                command_execution_info: CommandExecutionInfoMiddlewareResult = (
                    self.sync_command_execution_info(entries)
                )
                if (command := command_execution_info.command) is None:
                    raise EmptyEntriesError("Nothing was entered.", cli=self)
            else:
                command_execution_info: CommandExecutionInfoMiddlewareResult = (
                    self.sync_command_execution_info(entries)
                )
                if (command := command_execution_info.command) is None:
                    raise CommandDoesNotExistError(
                        f"Command {entries[0]} does not exist.", cli=self
                    )

            return_value: Any
            command, return_value = self._middleware_manager.sync_executor(
                command, command_execution_info.arg_entries, self._parser
            )
            return_value = self._middleware_manager.sync_return_value(
                command, return_value
            )
        except CLIError as cli_error:
            has_no_info: bool = cli_error.cli is None and cli_error.command is None
            was_self: bool = cli_error.cli is self
            if cli_error.cli is None:
                cli_error.cli = self
            if cli_error.command is None:
                cli_error.command = command
            return_value = self.middlewares.sync_error(command, cli_error)

            if return_value is CLI.RAISE:
                if has_no_info or was_self:
                    raise
                else:
                    raise CLIError(
                        *cli_error.args, cli=self, command=command
                    ) from cli_error
            elif return_value is CLI.REPLACE:
                cli_error.cli = self
                cli_error.command = command
                raise
        except Exception as error:
            return_value = self.middlewares.sync_error(command, error)
            if return_value in (CLI.RAISE, CLI.REPLACE):
                raise CLIError(
                    f"An exception was raised running {command.name}: {error}"
                    if command
                    else "An exception was raised attempting to execute a command.",
                    cli=self,
                    command=command,
                ) from error

        return return_value

    async def async_exec(self, entries: Sequence[str]) -> Any:
        """
        Execute a command from specified `entries`, asynchronously.
        :param entries: Command name (default middleware behavior) and arguments.
        :return: Command function return value
        """

        await self
        command: Command | None = None
        try:
            if not entries:
                command_execution_info: CommandExecutionInfoMiddlewareResult = (
                    await self.async_command_execution_info(entries)
                )
                if (command := command_execution_info.command) is None:
                    raise EmptyEntriesError("Nothing was entered.", cli=self)
            else:
                command_execution_info: CommandExecutionInfoMiddlewareResult = (
                    await self.async_command_execution_info(entries)
                )
                if (command := command_execution_info.command) is None:
                    raise CommandDoesNotExistError(
                        f"Command {entries[0]} does not exist.", cli=self
                    )

            return_value: Any
            command, return_value = await self._middleware_manager.async_executor(
                command, command_execution_info.arg_entries, self._parser
            )
            return_value = await self._middleware_manager.async_return_value(
                command, return_value
            )
        except CLIError as cli_error:
            has_no_info: bool = cli_error.cli is None and cli_error.command is None
            was_self: bool = cli_error.cli is self
            if cli_error.cli is None:
                cli_error.cli = self
            if cli_error.command is None:
                cli_error.command = command
            return_value = await self.middlewares.async_error(command, cli_error)

            if return_value is CLI.RAISE:
                if has_no_info or was_self:
                    raise
                else:
                    raise CLIError(
                        *cli_error.args, cli=self, command=command
                    ) from cli_error
            elif return_value is CLI.REPLACE:
                cli_error.cli = self
                cli_error.command = command
                raise
        except Exception as error:
            return_value = await self.middlewares.async_error(command, error)
            if return_value in (CLI.RAISE, CLI.REPLACE):
                raise CLIError(
                    f"An exception was raised running {command.name}: {error}"
                    if command
                    else "An exception was raised attempting to execute a command.",
                    cli=self,
                    command=command,
                ) from error

        return return_value

    def sync_prompt(self) -> Any:
        """
        Prompt the user for entries to `exec` on this CLI, synchronously.
        :return: Command function return value
        """

        return self.sync_exec(
            self._middleware_manager.sync_split(
                self._middleware_manager.sync_prompt(self.prompt_entry_marker)
            )
        )

    async def async_prompt(self) -> Any:
        """
        Prompt the user for entries to `exec` on this CLI, asynchronously.
        :return: Command function return value
        """

        await self
        return await self.async_exec(
            await self._middleware_manager.async_split(
                await self._middleware_manager.async_prompt(self.prompt_entry_marker)
            )
        )

    def __await__(self) -> Generator[Any, None, CLI]:
        if self.is_async:
            raise NotImplementedError

        raise RuntimeError(
            "This object is only to be awaited if it is the asynchronous implementation."
        )


__all__ = ["CLI", "ErrorHandler", "ReturnValueHandler"]
