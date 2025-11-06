class AudioNormaliser:
    """
    Handles audio normalisation parameters for sermon audio processing (default to Netflix standard - usually used at NHBC Balmoral).
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