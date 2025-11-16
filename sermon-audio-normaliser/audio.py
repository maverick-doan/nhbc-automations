import subprocess
from pathlib import Path
import json

class AudioNormaliser:
    """
    Handles audio normalisation parameters for sermon audio processing (default to Netflix standard).
    Default parameters (at NHBC Balmoral):
        - Target LUFS: -27.0
        - True Peak: -2.0 dBTP
        - Loudness Range: 7.0 LU
        - Audio Codec: aac
        - Audio Bitrate: 192k
    """
    def __init__(
        self, 
        target_lufs : float = -27.0,
        true_peak : float = -2.0,
        loudness_range : float = 7.0,
        audio_codec : str = "aac",
        audio_bitrate : str = "192k"
    ):
        """
        Initialises the AudioNormaliser with specified parameters.
        
        Parameters:
            target_lufs (float): Target loudness in LUFS.
            true_peak (float): Maximum true peak level in dBTP.
            loudness_range (float): Desired loudness range in LU.
            audio_codec (str): Audio codec to use for output.
            audio_bitrate (str): Bitrate for the output audio.
        """
        self.target_lufs = target_lufs
        self.true_peak = true_peak
        self.loudness_range = loudness_range
        self.audio_codec = audio_codec
        self.audio_bitrate = audio_bitrate

    # Helpers methods

    @staticmethod
    def _run_command(command: str | list[str]) -> None:
        return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    
    @staticmethod
    def _check_ffmpeg_installed() -> bool:
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        
    def analyse_audio(self, input_file: Path) -> dict:
        command = [
            "ffmpeg",
            "-i", str(input_file),
            "-af", f"loudnorm=I={self.target_lufs}:TP={self.true_peak}:LRA={self.loudness_range}:print_format=json",
            "-f", "null",
            "-"
        ]
        result = self._run_command(command)
        json_start = result.stderr.find('{')
        if json_start == -1:
            raise ValueError("Loudness analysis failed, no JSON output found.")
        json_blob = result.stderr[json_start:]
        return json.loads(json_blob)
