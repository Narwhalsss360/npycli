# Annotations

Conceptually, `Command` objects are a wrapper around function objects, where invocation with specific arguments as strings get parsed and get passed to the function each parameters expected types. That is, if the parameters of the function were annotated. If the parameters are not annotated, the default type of any parameter is `str`.

> [!NOTE]
> The following examples show basic string concatenation functions that may be wrapped with a `Command` object.

_The most basic definition:_

```python
def concat(str1, str2):
    return str1 + str2
```

_A better annotated definition:_

```python
def concat(str1: str, str2: str) -> str:
    return str1 + str2
```

The functions may be wrapped by using `npycli.Command.create(concat)` and invoked by passing a list of arguments to be parsed. Suppose we have assigned our `Command.create`ed function to a variable `cmd`, we may invoked by:

```python
print(cmd.exec_with(["A + ", "B"], {}))`
```

> [!NOTE]
> The following example shows a sum command.

> [!CAUTION]
> By default, not string types are parsed by passing the string to the constructor, _unless_ a custom parser is provided.

```python
def sum_function(n1: int, n2: int) -> int:
    return n1 + n2


sum_cmd: Command = npycli.Command.create(sum_function)
total: int = cmd_cmd.exec_with(["12", "5"], {})
print(total)
```

_We could also use `float` annotations to support floating-point numbers._

```python
def sum_function(n1: float, n2: float) -> float:
    return n1 + n2


sum_cmd: Command = npycli.Command.create(sum_function)
total: float = cmd_cmd.exec_with(["12.125", "5.5"], {})
prfloat(total)
```

# More on Parameter Kinds

Python supports the following parameter kinds:

- POSITIONAL_ONLY
- POSITIONAL_OR_KEYWORD
- VAR_POSITIONAL
- KEYWORD_ONLY
- VAR_KEYWORD

Which are all considered by the `npycli.parameters.parse_parameters` function which is the parser for the current version.

- POSITIONAL_ONLY _Parameters that appear before the `/`. By default, it appears before all parameters, that is, by default no parameters are positional only._
    - These parameters must not be passed by keyword, _only_ by position.
- POSITIONAL_OR_KEYWORD _Parameters that appear after `/` but before `*`._
    - These parameters may be passed by keyword _or_ by position.
- VAR_POSITIONAL _The `*` parameter._
    - This parameter kind allows for any number of positional arguments to be passed.
- KEYWORD_ONLY _Parameters that appear after `*` or `**`._
    - This parameter kind may not be passed positionally, _only_ by keyword
- VAR_KEYWORD _The `**` parameter._
    - This parameter kind allows for an number of keyword arguments to be passed.

> [!NOTE]
> `typing.Annotated` may be used for any annotation to add extra information.

**Kinds of `CommandParameterType`**

- `type`
- `TypeAliasType`
- `GenericAlias`

The list of all supported types and _kinds_ **(not discriminated by parameter kind)**

- Any plain type (that is not a `GenericAlias`)
- Any `TypeAlias` as long as it aliases a supported plain type or supported `GenericAlias`; _or_ there exists a custom parser, _an exception will be raised if `parse_parameters` is not supplied a custom parser._
- Any `GenericAlias` as long as there's a custom parser.
- Container types
    - Multiple arguments may be supplied to this parameter. _This is unrelated to the VAR_POSITIONAL parameter kind_
    - Must be annotated as `list[T]` or `tuple[T, ...]`.
    - Valid `T`s (item types) are any plain type, `TypeAlias` or `GenericAlias`.
- `BypassParse`
    - This must be the _only_ parameter for a command, if this is the type of a parameter, all of the entries that gets passed to the parser simply gets passed to the command. This _must_ be a VAR_POSITIONAL, for example a valid definition is `def f(args: *BypassParse): ...`. `BypassParse` is an alias of string, that is, `args` is a `tuple[str]`.

**Usage of These Parameter Kinds with `CommandParameterType` Kinds**

- POSITIONAL_ONLY
    - May be used with any plain type
    - May be used with any `TypeAliasType` that aliases a plain type. _Custom parser required if parsing fails with the aliased type._
    - May be used with any `GenericAlias` _custom parser is required._
- POSITIONAL_OR_KEYWORD `May be used with any supported type`
    - May be used with any plain type
    - May be used with any `TypeAliasType` that aliases a plain type. _Custom parser required if parsing fails with the aliased type._
    - May be used with any `GenericAlias` _custom parser is required._
- VAR_POSITIONAL
    - May be used with any plain type
    - May be used with any `TypeAliasType` that aliases a plain type. _Custom parser required if parsing fails with the aliased type._
    - May be used with any `GenericAlias` _custom parser is required._
- KEYWORD_ONLY `May be used with any supported`
    - May be used with any plain type
    - May be used with any `TypeAliasType` that aliases a plain type. _Custom parser required if parsing fails with the aliased type._
    - May be used with any `GenericAlias` _custom parser is required._
    - May be used with a valid Container Type.
- VAR_KEYWORD `May be used with any supported type`
    - May be used with any plain type
    - May be used with any `TypeAliasType` that aliases a plain type. _Custom parser required if parsing fails with the aliased type._
    - May be used with any `GenericAlias` _custom parser is required._
    - May be used with a valid Container Type.

**`Literal`s**

Literals are also supported, though you must use `npycli.parsing.create_literal_parser(literal_type: TypeAliasType | UnionType)`.

**Boolean Flags**

`parse_parameters` supports boolean flags. A boolean flag annotation should be of the plain type `bool` _and must a keyword parameter_ and no value needs to be provided.

# typing.Annotated


Usage of `typing.Annotated` is supported to declaratively add information to a parameter. Supported parameter metadata types are:

- `Alias`
    - Add more names to a parameter, or even set as `private_name` to hide the declared parameter name.
- `Description`
    - Add a description to a parameter.
- `AnnotationPreview`
    - Specify what the annotation preview should be _for *\_parameter_help()_ instead of the default behavior of the annotation being copied.
- `DefaultPreview`
    - Specify what the default value preview should be _for *\_parameter_help()_ instead of the default behavior of the default value being `repr`'d.
- `ParseHooks`
    - Specify a function that mutates the behavior of parsing by specifying `pre`, `post` and `err`.
- `CustomAttrbute`
    - Add a custom attribute to parameter

> [!NOTE]
> The following is an example from [reptil](https://codeberg.org/Narwhalsss360/reptil)

```python
@ignore_cli.cmd(help="Create templates")
async def template(
    *templates: str,
    source: Annotated[
        Optional[list[SourceSpec]],
        AnnotationPreview(f"{SOURCE_SPEC_ANNOTATION_PREVIEW}..."),
        DefaultPreview("<configured>")
    ] = None,
    strict: bool = False,
    domain: Annotated[
        Optional[list[SchemeDomain]],
        AnnotationPreview("SchemeDomain..."),
        DefaultPreview("*")
    ] = None,
    separator: Annotated[
        str,
        Description("The separator between templates")
    ] = "\n",
    header: Annotated[
        str,
        Description("The header for the template. Use {} for the template name")
    ] = "# > {}",
    footer: Annotated[
        str,
        Description("The footer for the template. Use {} for the template name")
    ] = "# < {}"
) -> None:
```

_Note, `SourceSpec` is the following `TypeAlias`: `type SourceSpec = int | str`. **It is important that `int` comes first, since `str` parsing will always succeed.** `SchemeDomain` is an `Enum`._

_basic help for `template` command (`$ reptil ignore help template`):_
```
template <*templates: str> <source: SourceSpec(source: str | by priority: int)... = <configured>> [strict] <domain: SchemeDomain... = *> <separator: str = '\n'> <header: str = '# > {}'> <footer: str = '# < {}'>
    Create templates
```

_basic help for `template` command (`$ reptil ignore help template --extended`):_
```
template
Parameters:
    templates
        Kind: VAR_POSITIONAL
        Annotation: str
        Types:
            str
    source
        Kind: KEYWORD_ONLY
        Annotation: SourceSpec(source: str | by priority: int)...
        Types:
            list
            None
        Default: <configured>
    strict
        Kind: KEYWORD_ONLY
        Annotation: bool
        Types:
            bool
        Default: False
    domain
        Kind: KEYWORD_ONLY
        Annotation: SchemeDomain...
        Types:
            list
            None
        Default: *
    separator
        Kind: KEYWORD_ONLY
        Annotation: str
        Types:
            str
        Default: '\n'
        Description: The separator between templates
    header
        Kind: KEYWORD_ONLY
        Annotation: str
        Types:
            str
        Default: '# > {}'
        Description: The header for the template. Use {} for the template name
    footer
        Kind: KEYWORD_ONLY
        Annotation: str
        Types:
            str
        Default: '# < {}'
        Description: The footer for the template. Use {} for the template name
Desciption: Create templates
```

_Note:_ There is no default help command implemented. You must implement your own, this help command was generated by:

```python
def get_properties(obj: Any) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    for name, member in getmembers(obj.__class__):
        if not isinstance(member, property):
            continue
        try:
            properties[name] = getattr(obj, name)
        except AttributeError:
            continue

    return properties


def get_fields_and_properties(obj: DataclassInstance) -> dict[str, Any]:
    return {
        **{
            field.name: getattr(obj, field.name, None) for field in fields(obj)
        },
        **get_properties(obj)
    }


def cmd_basic_help_with_help_text(cmd: Command) -> str:
    if cmd.help is None:
        return cmd.basic_command_help()

    return f"{cmd.basic_command_help()}\n{TAB_STRING}{cmd.help.replace("\n", f"\n{TAB_STRING}")}"


def make_help_cmd(cli: CLI, cli_description: str) -> Command:
    def help_cmd(
        command_name: Annotated[Optional[str], Alias("command-name", private=True)] = None,
        parameter_name: Annotated[Optional[str], Alias("parameter-name", private=True)] = None,
        extended: bool = False,
        properties: bool = False
    ) -> str:
        if extended and properties:
            raise NotImplementedError()

        if extended:
            command_help, parameter_help = Command.extended_command_help, CommandParameter.extended_parameter_help
        else:
            command_help, parameter_help = cmd_basic_help_with_help_text, CommandParameter.basic_parameter_help

        if command_name is None:
            if properties:
                raise NotImplementedError()

            return "\n\n".join([
                cli_description,
                *[command_help(cmd) for cmd in cli.commands]
            ])

        if (command := cli.get_command(command_name)) is None:
            return f"{command_name} is not a command."

        if parameter_name is not None:
            if (parameter := next(filter(lambda p: parameter_name in p.names, command.parameters), None)) is None:  # type: ignore
                return f"'{parameter_name}' is not a parameter"
            if properties:
                return "\n".join([f"{prop}: {val}" for prop, val in get_fields_and_properties(parameter).items()])
            return parameter_help(parameter)

        if properties:
            return "\n".join([f"{prop}: {val}" for prop, val in get_fields_and_properties(command).items()])
        return command_help(command)

    return Command.create(
        help_cmd,
        names=(
            "help",
            "h"
        ),
        help=(
            "<   >: Positional or keyword argument\n"
            "<*   >: Variable positional\n"
            "<**   >: Variable keyword\n"
            "/: Positional-keyword only delimiter\n"
            "<:    >: Parameter type\n"
            "<: =    >: Default value\n"
            "[   ]: Boolean flag (keyword only, no value needed)\n"
            f"Keyword prefix: {cli.kwarg_prefix}"
        ),
        kwarg_prefix=cli.kwarg_prefix
    )
```

_Parameter properties for `template source` command (`$ reptil ignore help template source --properties`):_
```
names: ('source',)
kind: KEYWORD_ONLY
annotation: typing.Annotated[list[SourceSpec] | None, AnnotationPreview(SourceSpec(source: str | by priority: int)...), DefaultPreview(<configured>)]
annotation_preview: SourceSpec(source: str | by priority: int)...
argument_types: (<class 'list'>, <class 'NoneType'>)
default: None
default_preview: <configured>
description: 
parse_hooks: None
argument_type: <class 'list'>
bypasses_parsing: False
container_type: <class 'list'>
custom_attributes: {}
is_plain: False
item_types: (SourceSpec,)
name: source
private_name: source

```
