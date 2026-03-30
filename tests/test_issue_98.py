"""Test for issue #98: Sound should play when stage is PAUSED_PENDING_INPUT"""

from yojenkins.yo_jenkins.status import Sound, StageStatus


class TestPausedInputSoundConfig:
    """Verify the sound infrastructure supports PAUSED_INPUT status"""

    def test_paused_input_sound_file_defined(self):
        """Sound.ITEMS must have a non-empty file for PAUSED_INPUT"""
        assert Sound.ITEMS.value['PAUSED_INPUT'] != ''

    def test_stage_status_paused_input_value(self):
        """StageStatus.PAUSED_INPUT must map to the Jenkins API string"""
        assert StageStatus.PAUSED_INPUT.value == 'PAUSED_PENDING_INPUT'

    def test_paused_input_sound_is_wav(self):
        """Sound file must be a .wav file"""
        assert Sound.ITEMS.value['PAUSED_INPUT'].endswith('.wav')
