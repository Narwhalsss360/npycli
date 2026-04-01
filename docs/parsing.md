# Parameter Parsing

The `Parameter` class is used to describe a parameter of a `Command`. Parsing is
done the following function in `npycli.parameter`

```python
def parse_parameters(
    parameters: list[CommandParameter],
    entries: list[str],
    keyword_prefix: str,
    argument_seperator: str,
    parsers: dict[CommandParameterType, Callable[[str], Any]]
) -> tuple[list[Any], dict[str, Any]]:
```

Notice support for and `argument_seperator`, if provided by and entry, all
following entries are treated as positional arguments. Also notice `parsers`,
custom parsers may be provided for custom types.

The `CommandParameterType` is used instead of `type` to support all `type`,
`TypeAliasType` and `GenericAliasType` so that aliases get parsed properly.

# Custom Parsers

A custom parser may be specified for any type of the union `CommandParameterType`. These are useful for any type that cannot be constructed by passing a string into its constructor.

> [!NOTE]
> There exists `npycli.parsing.create_literal_parser(literal_type: TypeAliasType | UnionType)` and `def create_enum_parser[T](enum_type: Type[T])` to help create parsers for `Literal` types and `Enum` types.
> Otherwise, thew following is an example of a custom parser


```python
TRUTHY: tuple[str, ...] = "y", "yes", "t", "true", "on", "enable", "enabled", "1", "continue"
FALSY: tuple[str, ...] = "n", "no", "f", "false", "off", "disable", "disable", "0", "cancel"


def bool_parser(s: str) -> bool:
    s = s.strip().lower()
    if s in TRUTHY:
        return True
    if s in FALSY:
        return False
    raise ParsingError(s, f"{s} was neither {repr(TRUTHY)} or {repr(FALSY)}")
```

---

See more on [Annotations](./annotations.md).
