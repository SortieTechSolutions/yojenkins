---
name: yojenkins-cli-command
description: Scaffolds new CLI commands following the yojenkins 3-layer pattern. Use when asked to "add a CLI command", "new command", or "add subcommand".
---

# yojenkins CLI Command Scaffold

Create new CLI commands following the established 3-layer architecture.

## Steps

1. **Identify the command group** (auth, server, node, account, credential, folder, job, build, stage, step, tools)
2. **Add Click command** in `yojenkins/cli_sub_commands/<group>.py`
3. **Add CLI handler** in `yojenkins/cli/cli_<group>.py`
4. **Add business logic** in `yojenkins/yo_jenkins/<module>.py`
5. **Wire up** in `yojenkins/__main__.py` if creating a new group

## Layer 1: Click Command (cli_sub_commands/<group>.py)

```python
@click.command(short_help='\tShort description of command')
@click.argument('arg_name', type=str)
@click.option('-o', '--option-name', type=str, default=None, help='Description')
@click.option('-f', '--flag-name', type=bool, is_flag=True, default=False, help='Description')
@format_output
@profile
@debug
@click.pass_context
def command_name(ctx, arg_name, option_name, flag_name, **kwargs):
    """Long description of what this command does."""
    kwargs = translate_kwargs(kwargs)
    cli_<group>.command_name(ctx, arg_name, option_name, flag_name, **kwargs)
```

## Layer 2: CLI Handler (cli/cli_<group>.py)

```python
def command_name(ctx, arg_name, option_name, flag_name, **kwargs):
    """Handle command_name CLI logic."""
    set_debug_log_level(kwargs)
    yj_obj = setup_yj_obj(kwargs)  # Auth + REST setup

    # Call business logic
    result = yj_obj.<module>.<method>(arg_name, option=option_name)

    # Format output
    standard_out(kwargs, result)
```

## Layer 3: Business Logic (yo_jenkins/<module>.py)

```python
def method(self, arg_name, option=None):
    """Description.

    Args:
        arg_name: Description
        option: Description

    Returns:
        dict or list or bool
    """
    logger.debug('Calling Jenkins API: %s', endpoint)
    # Implementation using self.rest
    return result
```

## Decorator Order (innermost to outermost)

1. `@click.pass_context` (innermost - closest to function)
2. `@debug`
3. `@profile`
4. `@format_output` (outermost)

## Conventions

- Use `translate_kwargs()` to rename reserved words (yaml->opt_yaml, json->opt_json)
- Tab-prefix short_help strings for alignment
- Use `click.secho()` for colored terminal output
- Show `ctx.get_help()` when required arguments are missing
- Never import Click in yo_jenkins/ business logic layer
- Use `@log_to_history` on CLI handlers
