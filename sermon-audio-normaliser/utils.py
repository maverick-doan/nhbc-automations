import subprocess
import shutil, os
from pathlib import Path
from tkinter import filedialog, Tk
import time
import msvcrt
import sys

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
    def get_onedrive_info() -> dict | None:
        """
        Get OneDrive process information including path and version.
        Returns dict with 'path', 'version', and 'is_running' keys, or None if not found.
        """
        try:
            # Check if OneDrive process is running
            check_process = """
            $OneDrive = Get-Process | Where-Object {$_.Name -like "*OneDrive*"} | Select-Object -First 1
            if ($OneDrive) {
                Write-Output "RUNNING"
                Write-Output $OneDrive.Path
            } else {
                Write-Output "NOT_RUNNING"
            }
            """
            
            result = subprocess.run(
                ["powershell", "-Command", check_process],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                text=True
            )
            
            lines = result.stdout.strip().split('\n')
            is_running = lines[0].strip() == "RUNNING"
            
            # Get OneDrive path (from running process or default location)
            onedrive_path = None
            if is_running and len(lines) > 1:
                onedrive_path = lines[1].strip()
            else:
                # Default OneDrive location
                default_path = Path("C:/Program Files/Microsoft OneDrive/OneDrive.exe")
                if default_path.exists():
                    onedrive_path = str(default_path)
            
            if not onedrive_path:
                return None
            
            # Get OneDrive version
            version_cmd = f"""
            $version = (Get-Command "{onedrive_path}").FileVersionInfo.ProductVersion
            Write-Output $version
            """
            
            version_result = subprocess.run(
                ["powershell", "-Command", version_cmd],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
                text=True
            )
            
            version = version_result.stdout.strip()
            
            return {
                'path': onedrive_path,
                'version': version,
                'is_running': is_running
            }
            
        except Exception as e:
            print(f"Error getting OneDrive info: {e}")
            return None
    
    @staticmethod
    def ensure_onedrive_running() -> bool:
        """
        Ensure OneDrive is running. If not, attempt to start it.
        Returns True if OneDrive is running, False otherwise.
        """
        info = WindowsUtils.get_onedrive_info()
        if not info:
            print("ERROR: OneDrive installation not found.")
            return False
        
        if info['is_running']:
            return True
        
        # Attempt to start OneDrive
        try:
            print("Starting OneDrive...")
            subprocess.Popen([info['path']], shell=False)
            time.sleep(5)  # Wait for OneDrive to start
            
            # Check again
            info = WindowsUtils.get_onedrive_info()
            if info and info['is_running']:
                print("OneDrive started successfully.")
                return True
            else:
                print("ERROR: Failed to start OneDrive.")
                return False
        except Exception as e:
            print(f"ERROR: Failed to start OneDrive: {e}")
            return False

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
    def timed_input(prompt: str, timeout: int = 60, default: str = 'y') -> str:
        """
        Get user input with a timeout. Returns default value if timeout expires.
        
        Parameters:
            prompt (str): The prompt to display to the user.
            timeout (int): Timeout in seconds.
            default (str): Default value to return on timeout.
        
        Returns:
            str: User input or default value on timeout.
        """
        sys.stdout.write(prompt)
        sys.stdout.flush()
        
        start_time = time.time()
        input_chars = []
        
        while True:
            elapsed = time.time() - start_time
            remaining = int(timeout - elapsed)
            
            if elapsed >= timeout:
                print(f"\nNo input received. Defaulting to '{default}'...")
                return default
            
            # Update countdown display
            if remaining > 0 and int(elapsed) != int(elapsed - 0.1):
                sys.stdout.write(f"\r{prompt}[{remaining}s] ")
                sys.stdout.flush()
            
            # Check for keyboard input
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Handle Enter key
                if char in (b'\r', b'\n'):
                    print()  # New line
                    return ''.join(input_chars).strip().lower()
                
                # Handle Backspace
                elif char == b'\x08':
                    if input_chars:
                        input_chars.pop()
                        sys.stdout.write('\r' + ' ' * (len(prompt) + len(input_chars) + 20))
                        sys.stdout.write(f"\r{prompt}[{remaining}s] {''.join(input_chars)}")
                        sys.stdout.flush()
                
                # Handle regular characters
                else:
                    try:
                        decoded = char.decode('utf-8')
                        if decoded.isprintable():
                            input_chars.append(decoded)
                            sys.stdout.write(decoded)
                            sys.stdout.flush()
                    except:
                        pass
            
            time.sleep(0.1)
    
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
    def sync_onedrive(file_path: Path, timeout: int = 1800) -> bool:
        """
        Trigger OneDrive sync and wait for file to be fully synced.
        
        Parameters:
            file_path (Path): The file to monitor for sync completion.
            timeout (int): Maximum time to wait for sync in seconds (default 30 minutes).
        
        Returns:
            bool: True if sync completed, False if timeout or error.
        """
        try:
            info = WindowsUtils.get_onedrive_info()
            if not info or not info['is_running']:
                print("ERROR: OneDrive is not running.")
                return False
            
            # Get OneDrive.Sync.Service path
            version = info['version']
            sync_service_path = Path(f"C:/Program Files/Microsoft OneDrive/{version}/OneDrive.Sync.Service.exe")
            
            if not sync_service_path.exists():
                print(f"WARNING: OneDrive.Sync.Service not found at {sync_service_path}")
                print("Sync may still proceed automatically.")
            else:
                # Trigger sync service
                try:
                    subprocess.Popen([str(sync_service_path)], shell=False)
                    print("OneDrive sync service triggered.")
                except Exception as e:
                    print(f"WARNING: Could not trigger sync service: {e}")
            
            # Wait a moment for sync to start
            time.sleep(5)
            
            # Monitor file attributes until sync is complete
            check_interval = 60  # Check every 1 minute
            start_time = time.time()
            
            print(f"Monitoring file sync status (checking every {check_interval} seconds)...")
            
            while (time.time() - start_time) < timeout:
                # Check file attributes
                check_cmd = f"""
                $file = Get-Item -Path "{file_path}" -Force
                $attributes = $file.Attributes -split ', '
                if ($attributes -contains 'Archive' -and $attributes -contains 'ReparsePoint') {{
                    Write-Output "SYNCED"
                }} else {{
                    Write-Output "SYNCING"
                    Write-Output $file.Attributes
                }}
                """
                
                result = subprocess.run(
                    ["powershell", "-Command", check_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=10,
                    text=True
                )
                
                output = result.stdout.strip()
                lines = output.split('\n')
                
                if lines[0] == "SYNCED":
                    print("File successfully synced to OneDrive!")
                    return True
                else:
                    elapsed = int(time.time() - start_time)
                    if len(lines) > 1:
                        attrs = lines[1]
                        print(f"  [{elapsed}s] File attributes: {attrs}")
                    else:
                        print(f"  [{elapsed}s] Still syncing...")
                
                time.sleep(check_interval)
            
            # Timeout reached
            print(f"WARNING: Sync monitoring timed out after {timeout} seconds.")
            print("File may still be syncing in the background.")
            return False
            
        except Exception as e:
            print(f"OneDrive sync error: {e}")
            return False