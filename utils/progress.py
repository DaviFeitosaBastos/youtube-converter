def make_progress_callback():
    def on_progress(stream, chunk, bytes_remaining):
        total = stream.filesize or 0
        if total <= 0:
            return
        downloaded = max(0, min(total, total - bytes_remaining))
        percent = downloaded / total * 100
        filled = int(30 * downloaded / total)
        bar = "#" * filled + "-" * (30 - filled)
        print(f"\r[{bar}] {percent:.1f}% | {downloaded / 1048576:.1f} MB / {total / 1048576:.1f} MB", end="", flush=True)
        if bytes_remaining <= 0:
            print()
    return on_progress
