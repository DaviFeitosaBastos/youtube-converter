from ui.display import cli, clear, headers
from ui.validation import yes_or_not, get_int_input, url_validate, vd_input_validated, track_input_validated, gif_input_validated
from service.video_service import download_high_res, download_low_res, get_video_info
from service.track_service import download_track_youtube
from service.gif_service import convert_mp4_to_gif
from ui.validation import pick_file
from utils.log_utils import get_base_dir

HEADER1 = "Video Download"
HEADER2 = "Track Download"
HEADER3 = "GIF Converter"

def videos_downloader_menu():
    """
    Display the video download menu and handle user input.

    Options:
        1 - Get higher resolution videos
        2 - Get lower resolution videos
        3 - Get the videos info
        0 - Back to main menu
    """
    sub_routes = {
        1: download_high_res,
        2: download_low_res,
        3: get_video_info,
    }

    while True:
        clear()
        headers(HEADER1)
        cli.print("[red]1[/red] - Get higher resolution videos")
        cli.print("[red]2[/red] - Get lower resolution videos")
        cli.print("[red]3[/red] - Get the videos info")
        cli.print("[red]0[/red] - [yellow]Back to main menu[/yellow]")

        input_choice = get_int_input()

        if input_choice is None:
            continue

        if input_choice == 0:
            clear()
            if yes_or_not("Wanna go back [Y/N]: "):
                break
            continue

        choice = vd_input_validated(input_choice)

        if not isinstance(choice, int):
            continue

        handler = sub_routes.get(choice)
        if handler:
            url = input("\nURL: ")
            if not url_validate(url):
                continue
            handler(url)



def tracks_downloader_menu():
    """
    Display the track download menu and handle user input.

    Options:
        1 - Get the track from [YOUTUBE]
        0 - Back to main menu
    """
    sub_routes = {
        1: download_track_youtube,
    }

    while True:
        clear()
        headers(HEADER2)
        cli.print("[purple]1[/purple] - Get the track from [red][[/red][red]YOU[/red]TUBE[red]][/red]")
        cli.print("[purple]0[/purple] - [yellow]Back to main menu[/yellow]")

        input_choice = get_int_input()

        if input_choice is None:
            continue

        if input_choice == 0:
            clear()
            if yes_or_not("Wanna go back [Y/N]: "):
                break
            continue

        choice = track_input_validated(input_choice)

        if not isinstance(choice, int):
            continue

        handler = sub_routes.get(choice)
        if handler:
            url = input("\nURL: ")
            if not url_validate(url):
                continue
            handler(url)

def gif_converter_menu():
    sub_routes = {
        1: convert_mp4_to_gif,
    }

    while True:
        clear()
        headers(HEADER3)
        cli.print("[cyan]1[/cyan] - Convert MP4 to GIF")
        cli.print("[cyan]0[/cyan] - [yellow]Back to main menu[/yellow]")

        input_choice = get_int_input()

        if input_choice is None:
            continue

        if input_choice == 0:  # ← check ANTES do validador
            clear()
            if yes_or_not("Wanna go back [Y/N]: "):
                break
            continue

        choice = gif_input_validated(input_choice)

        if not isinstance(choice, int):
            continue

        handler = sub_routes.get(choice)
        if handler:
            folder = get_base_dir() / "videos"
            path_input = input("MP4 path (Enter to choose from downloads): ").strip().strip('"')
            path = path_input or pick_file(folder, ".mp4")
            if path:
                handler(str(path))

# Route map: menu option -> handler function
routes = {
    1: videos_downloader_menu,  # Video downloader
    2: tracks_downloader_menu,  # Track downloader
    3: gif_converter_menu,
}

if __name__ == "__main__":
    videos_downloader_menu()
