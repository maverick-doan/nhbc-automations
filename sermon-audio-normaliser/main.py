import sys
from pathlib import Path
from datetime import datetime
from audio import AudioNormaliser
from utils import WindowsUtils
from zoneinfo import ZoneInfo

def main():
    """
    Main script for one-click audio normalisation with automatic shutdown.
    """
    print("=" * 60)
    print("NHBC Sermon Audio Normaliser")
    print("=" * 60)
    print()
    
    # Check if FFmpeg is installed
    if not AudioNormaliser._check_ffmpeg_installed():
        print("ERROR: FFmpeg is not installed or not in PATH.")
        print("Please install FFmpeg first: https://ffmpeg.org/download.html")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Select input file
    print("Step 1: Select the sermon video/audio file to normalise...")
    input_file = WindowsUtils.select_file(title="Select Sermon File")
    
    if not input_file:
        print("No file selected. Exiting...")
        input("\nPress Enter to exit...")
        sys.exit(0)
    
    print(f"Selected: {input_file.name}")
    print()
    
    # Create output filename with timestamp
    timestamp = datetime.now(tz=ZoneInfo("Australia/Brisbane")).strftime("%Y_%m_%d")
    output_file = input_file.parent / f"NHBC_Bal_{timestamp}_Normalised_Audio"
    
    print(f"Output will be saved to: {output_file.name}")
    print()
    
    # Confirm before proceeding
    print("=" * 60)
    print("Ready to start normalisation process")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print()
    print("Settings:")
    print("  - Target LUFS: -27.0")
    print("  - True Peak: -2.0 dBTP")
    print("  - Loudness Range: 7.0 LU")
    print("  - Audio Codec: AAC")
    print("  - Audio Bitrate: 192k")
    print()
    
    response = input("Continue? (y/n): ").strip().lower()
    if response != 'y':
        print("Cancelled by user.")
        input("\nPress Enter to exit...")
        sys.exit(0)
    
    print()
    print("=" * 60)
    print("Starting normalisation process...")
    print("=" * 60)
    
    try:
        # Initialise normaliser with NHBC Balmoral defaults
        normaliser = AudioNormaliser()
        
        # Run normalisation
        print("Pass 1: Analysing audio levels...")
        stats = normaliser.analyse_audio(input_file)
        print(f"  Input Loudness: {stats['input_i']} LUFS")
        print(f"  Input True Peak: {stats['input_tp']} dBTP")
        print(f"  Input Loudness Range: {stats['input_lra']} LU")
        print()
        
        print("Pass 2: Applying normalisation...")
        normaliser.normalise_audio(input_file, output_file)
        
        print()
        print("=" * 60)
        print("SUCCESS! Normalisation complete.")
        print("=" * 60)
        print(f"Output file: {output_file}")
        print()
        
        # Ask about shutdown
        shutdown = input("Shutdown computer now? (y/n): ").strip().lower()
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < 120:
            if shutdown == 'y':
                delay = 30
                print(f"\nShutting down in {delay} seconds...")
                print("Close this window to cancel shutdown.")
                WindowsUtils.shutdown_computer(delay_seconds=delay)
                input("\nPress Enter to exit...")
            else:
                print("\nShutdown cancelled. You can close this window.")
                input("\nPress Enter to exit...")
        print("\nNo shutdown confirmed. Automatic shutdown assumed.")
        WindowsUtils.shutdown_computer(delay_seconds=30)
        input("\nPress Enter to exit...")
    
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    except Exception as e:
        print(f"\nERROR: An unexpected error occurred:")
        print(f"{type(e).__name__}: {e}")
        WindowsUtils.cancel_shutdown()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()