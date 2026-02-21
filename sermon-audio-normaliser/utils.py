import subprocess
import shutil, os
from pathlib import Path
from tkinter import filedialog, Tk
import time

class WindowsUtils:
    """Utility functions for Windows operations."""
    @staticmethod
    def secure_binary_search(binary_name: str) -> str | None:
        """
        Check if a binary is available in the system PATH.
        """
        system_path = os.environ.get("PATH", "")
        try:
            binary_path = shutil.which(binary_name, path=system_path)
            if binary_path:
                return binary_path
        except Exception:
            return None
        return None

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
    
    @staticmethod
    def select_folder(title: str = "Select a folder") -> Path | None:
        """
        Open a folder dialog for user to select an output folder.
        """
        root = Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory(title=title)
        root.destroy()
        return Path(folder_path) if folder_path else None
    
    @staticmethod
    def _get_onedrive_roots() -> list[Path]:
        """
        Return list of OneDrive root directories from environment.
        """
        roots = []
        for var in ("OneDrive", "OneDriveCommercial", "OneDriveConsumer"):
            val = os.environ.get(var)
            if val:
                try:
                    roots.append(Path(val).resolve())
                except Exception:
                    continue
        return roots
    
    @staticmethod
    def is_path_in_onedrive(path: Path) -> bool:
        """
        Return True if given path is inside any detected OneDrive root.
        """
        try:
            p = Path(path).resolve()
        except Exception:
            return False
        for root in WindowsUtils._get_onedrive_roots():
            try:
                if hasattr(p, "is_relative_to"):
                    if p.is_relative_to(root):
                        return True
                else:
                    if str(p).startswith(str(root)):
                        return True
            except Exception:
                continue
        return False
    
    @staticmethod
    def sync_onedrive(timeout: int = 300) -> bool:
        """
        Trigger OneDrive sync and wait for completion.
        
        Parameters:
            timeout (int): Maximum time to wait for sync in seconds.
        
        Returns:
            bool: True if sync completed, False if timeout or error.
        """
        try:
            # Start OneDrive sync via PowerShell
            # This triggers the sync process
            ps_command = """
            $OneDrive = Get-Process | Where-Object {$_.Name -like "*OneDrive*"}
            if ($OneDrive) {
                Start-Process "odopen://sync"
            }
            """
            
            subprocess.run(
                ["powershell", "-Command", ps_command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )
            
            # Wait a moment for sync to start
            time.sleep(5)
            
            # Monitor OneDrive sync status
            start_time = time.time()
            while (time.time() - start_time) < timeout:
                # Check if OneDrive is syncing
                check_command = """
                $Shell = New-Object -ComObject Shell.Application
                $OneDrive = $Shell.NameSpace($env:OneDrive)
                if ($OneDrive) {
                    $Status = $OneDrive.Self.Name
                    if ($Status -notmatch "Syncing") {
                        exit 0
                    }
                }
                exit 1
                """
                result = subprocess.run(
                    ["powershell", "-Command", check_command],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=5
                )
                
                if result.returncode == 0:
                    return True
                
                time.sleep(5)
            
            # Timeout reached
            return False
            
        except Exception as e:
            print(f"OneDrive sync error: {e}")
            return False