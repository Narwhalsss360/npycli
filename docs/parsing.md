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

The `CommandParameterType` is used instead of `type` to support both `type`
and `TypeAliasType` so that aliases get parsed properly.


