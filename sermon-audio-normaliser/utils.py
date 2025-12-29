import subprocess
import sys
from pathlib import Path
from tkinter import filedialog, Tk

class WindowsUtils:
    """Utility functions for Windows operations."""
    
    @staticmethod
    def shutdown_computer(delay_seconds: int = 60):
        """
        Schedule Windows shutdown after specified delay (after audio processing).
        """
        try:
            subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)], check=True)
            print(f"Computer will shutdown in {delay_seconds} seconds...")
        except subprocess.CalledProcessError as e:
            print(f"Failed to schedule shutdown: {e}")
    
    @staticmethod
    def cancel_shutdown():
        """Cancel a scheduled shutdown."""
        try:
            subprocess.run(["shutdown", "/a"], check=True)
            print("Shutdown cancelled.")
        except subprocess.CalledProcessError:
            print("No shutdown to cancel.")
    
    @staticmethod
    def select_file(title: str = "Select a file", filetypes: list = None) -> Path | None:
        """
        Open a file dialog for user to select a file.
        """
        if filetypes is None:
            filetypes = [
                ("Video files", "*.mp4 *.mov *.avi *.mkv"),
                ("Audio files", "*.mp3 *.wav *.aac *.m4a"),
                ("All files", "*.*")
            ]
        
        root = Tk()
        root.withdraw()  # Hide the main window
        root.attributes('-topmost', True)  # Bring dialog to front
        
        file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        
        return Path(file_path) if file_path else None