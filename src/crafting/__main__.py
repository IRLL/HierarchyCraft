from crafting.cli import crafting_cli
from crafting.render.human import render_env_with_human


def main():
    """Run crafting command line interface."""
    env = crafting_cli()
    render_env_with_human(env)


if __name__ == "__main__":
    main()
