"""Shows a live simulation of the clock state through a web interface"""
from nicegui import ui, app
from pathlib import Path


def startup() -> None:
    print('In startup')
    a = 1/ 0

    @ui.page('/')
    def home() -> None:
        ui.label('Hello world')

def start() -> None:
    """Start the simulation"""
    print('Starting live view server')
    root_path = Path(__file__).parent
    app.add_static_files('/static', root_path / 'images')
    app.on_startup(lambda: startupx())
    ui.run(port=8100, storage_secret='super secret storage')

