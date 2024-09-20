import os.path
import subprocess
from pathlib import Path
import time

import rcssmin
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers.polling import PollingObserver


def _build_css(main_scss_file: Path, dest_css_file: Path, build_dir: Path):
    # Compile with SCSS.
    tmp_css_file: Path = build_dir / 'app.css'
    subprocess.run(['sass', str(main_scss_file), str(tmp_css_file)])

    # Minify!
    with open(tmp_css_file, 'r') as f:
        raw_css: str = f.read()

    with open(dest_css_file, 'w') as f:
        f.write(rcssmin.cssmin(raw_css))


def _build_js(main_js_file: Path, dest_js_file: Path):
    # --minify has been disabled to help with development, since esbuild
    # removes calls to console.log() when minify is on. Later on, we
    # can set minify on by default when we're building for production.
    subprocess.run([
        'esbuild',
        str(main_js_file),
        '--bundle',
        # '--minify',
        f'--outfile={str(dest_js_file)}'
    ])


class CSSHandler(FileSystemEventHandler):
    def __init__(self,
                 main_scss_file: Path,
                 dest_css_file: Path,
                 build_dir: Path):
        self.main_scss_file = main_scss_file
        self.dest_css_file = dest_css_file
        self.build_dir = build_dir

    def on_any_event(self, event: FileSystemEvent):
        print(f':: [CSS] Changes detected in {event.src_path}. Rebuilding...')
        _build_css(self.main_scss_file, self.dest_css_file, self.build_dir)


class JSHandler(FileSystemEventHandler):
    def __init__(self, main_js_file, dest_js_file):
        self.main_js_file = main_js_file
        self.dest_js_file = dest_js_file

    def on_any_event(self, event: FileSystemEvent) -> None:
        print(f':: [JS] Changes detected in {event.src_path}. Rebuilding...')

        _build_js(self.main_js_file, self.dest_js_file)


def main():
    # TODO: - Add an option to set the asset builder mode to development or
    #         production. When it's set to development, minify will be
    #         disabled. When it's set to production, it should be enabled.
    #       - The default action of the asset builder is to just build the
    #         assets and be done with it. We should implement that later on.
    #         We should add a --watch option later too, which will make it
    #         watch assets we're editing.
    dest_dir: Path = Path('py/compmatrix/client/assets/dist')

    scss_dir: Path = Path('py/compmatrix/client/assets/raw/scss')
    css_build_dir: Path = Path('py/compmatrix/client/assets/build/css')
    main_scss_file: Path = scss_dir / 'app.scss'
    dest_css_file: Path = dest_dir / 'app.css'

    js_dir: Path = Path('py/compmatrix/client/assets/raw/js')
    main_js_file: Path = js_dir / 'app.js'
    dest_js_file: Path = dest_dir / 'app.js'

    print('🟩 Starting asset builder...')

    print('🔨 Building assets...')

    print(':: Building CSS assets...')
    _build_css(main_scss_file, dest_css_file, css_build_dir)

    print(':: Building JS assets...')
    _build_js(main_js_file, dest_js_file)

    print('💖 Done!')

    print(f'🔭 Watching SCSS directory: {str(scss_dir)}')
    css_handler: CSSHandler = CSSHandler(main_scss_file,
                                         dest_css_file,
                                         css_build_dir)

    print(f'🔭 Watching JS directory: {str(js_dir)}')
    js_handler: JSHandler = JSHandler(main_js_file, dest_js_file)

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
