import wave
from pathlib import Path

class AudioProcessor:
    """Handles WAV file concatenation and audio processing."""
    
    @staticmethod
    def concatenate_wav_files(wav_files: list[Path], output_path: Path, 
                            pause_between: float = 0.0) -> None:
        """Concatenate multiple WAV files with optional pauses."""
        if not wav_files:
            raise ValueError("No WAV files to concatenate")
            
        # Get format from first file
        with wave.open(str(wav_files[0]), "rb") as ref:
            channels = ref.getnchannels()
            sample_width = ref.getsampwidth() 
            frame_rate = ref.getframerate()
        
        with wave.open(str(output_path), "wb") as out_wf:
            out_wf.setnchannels(channels)
            out_wf.setsampwidth(sample_width)
            out_wf.setframerate(frame_rate)
            
            for i, wav_file in enumerate(wav_files):
                AudioProcessor._append_wav(out_wf, wav_file)
                
                # Add pause between files (except last)
                if pause_between > 0 and i < len(wav_files) - 1:
                    AudioProcessor._write_silence(out_wf, pause_between, frame_rate)
    
    @staticmethod
    def _append_wav(dst_wf: wave.Wave_write, src_wav: Path) -> None:
        """Append WAV file content to destination."""
        with wave.open(str(src_wav), "rb") as src_wf:
            # Verify format compatibility
            assert src_wf.getnchannels() == dst_wf.getnchannels()
            assert src_wf.getsampwidth() == dst_wf.getsampwidth()
            assert src_wf.getframerate() == dst_wf.getframerate()
            
            frames = src_wf.readframes(src_wf.getnframes())
            dst_wf.writeframes(frames)
    
    @staticmethod
    def _write_silence(dst_wf: wave.Wave_write, seconds: float, sample_rate: int) -> None:
        """Write silence to WAV file."""
        if seconds <= 0:
            return
        n_samples = int(seconds * sample_rate)
        silence = b"\x00\x00" * n_samples
        dst_wf.writeframes(silence)