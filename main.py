# Display imports
from ui.display import cli, clear, headers, main_menu, loading, print_exit
# Validation imports
from ui.validation import get_int_input, main_input_validated
# ROUTER import
from router import routes
# SYSTEM import
import sys


def main():
    """
    Main application loop. Handles navigation between menus.
    """
    HEADER = "Main menu"

    loading()

    # Run the program loop
    while True:
        clear()
        headers(HEADER)
        main_menu()

        input_choice = get_int_input()

        if input_choice is None:
            continue

        choice = main_input_validated(input_choice)

        if not isinstance(choice, int):
            continue

        if input_choice == 0:
            print_exit()
            sys.exit()

        # Dispatch to the selected menu handler
        handler = routes.get(choice)
        if handler:
            handler()


def run():
    if "--check" in sys.argv:
        from utils.media import require_ffmpeg
        try:
            require_ffmpeg()
        except FileNotFoundError:
            cli.print("FFmpeg não encontrado no PATH.")
            return 1
        cli.print("Tudo pronto: dependências do Python e FFmpeg disponíveis.")
        return 0
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        cli.print("\nAté a próxima!")
    return 0


if __name__ == "__main__":
    sys.exit(run())
