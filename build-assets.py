import os.path
import subprocess
from pathlib import Path
import time

import rcssmin
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers.polling import PollingObserver


class CSSHandler(FileSystemEventHandler):
    def __init__(self,
                 base_scss_dir: Path,
                 css_build_dir: Path,
                 dist_dir: Path):
        self.scss_dir = base_scss_dir
        self.css_build_dir = css_build_dir
        self.dist_dir = dist_dir

    def on_any_event(self, event: FileSystemEvent):
        print(f':: [CSS] Changes detected in {event.src_path}. Rebuilding...')

        # Compile with SCSS.
        main_scss_file: Path = self.scss_dir / 'app.scss'
        dest_css_file: Path = self.css_build_dir / 'app.css'
        subprocess.run(['sass', str(main_scss_file), str(dest_css_file)])

        # Minify!
        minified_css_file: Path = self.dist_dir / 'app.css'
        with open(dest_css_file, 'r') as f:
            raw_css: str = f.read()

        with open(minified_css_file, 'w') as f:
            f.write(rcssmin.cssmin(raw_css))


class JSHandler(FileSystemEventHandler):
    def __init__(self, js_dir, dist_dir):
        self.js_dir = js_dir
        self.dist_dir = dist_dir

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f':: [JS] Changes detected in {event.src_path}. Rebuilding...')

        main_js_file: Path = self.js_dir / 'app.js'
        dest_js_file: Path = self.dist_dir / 'app.js'
        subprocess.run([
            'esbuild',
            str(main_js_file),
            '--bundle',
            '--minify',
            f'--outfile=={str(dest_js_file)}'
        ])


def main():
    dest_dir: Path = Path('py/compmatrix/client/assets/dist')

    scss_dir: Path = Path('py/compmatrix/client/assets/raw/scss')
    css_build_dir: Path = Path('py/compmatrix/client/assets/build/css')

    js_dir: Path = Path('py/compmatrix/client/assets/raw/js')

    print('🟩 Starting asset builder...')

    print(f'🔭 Watching SCSS directory: {str(scss_dir)}')
    css_handler: CSSHandler = CSSHandler(scss_dir, css_build_dir, dest_dir)

    print(f'🔭 Watching JS directory: {str(js_dir)}')
    js_handler: JSHandler = JSHandler(js_dir, dest_dir)

    # We're using PollingObserver for now since we're coding in Windows, but
    # running things inside WSL 2. File notification support between Windows
    # and WSL is not yet added in the Windows 9P servers. For details, see:
    #   https://youtu.be/lwhMThePdIo?si=NW7fBHIQN7iOosKR&t=3166
    css_observer: PollingObserver = PollingObserver()
    js_observer: PollingObserver = PollingObserver()

    css_observer.schedule(css_handler, path=str(scss_dir), recursive=True)
    js_observer.schedule(js_handler, path=str(js_dir), recursive=True)

    css_observer.start()
    js_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('🟥 Shutting down asset builder...')
    finally:
        css_observer.stop()
        js_observer.stop()

        css_observer.join()
        js_observer.join()


if __name__ == '__main__':
    main()
