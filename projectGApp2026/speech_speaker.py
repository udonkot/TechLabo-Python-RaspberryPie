import azure.cognitiveservices.speech as speechsdk


class SpeechSpeaker:
    """Azure AI Speech で識別結果を音声合成し、スピーカーから応答する"""

    def __init__(self, key, region, voice, language):
        if not key or not region:
            raise ValueError('AZURE_SPEECH_KEY / AZURE_SPEECH_REGION が設定されていません')

        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        speech_config.speech_synthesis_voice_name = voice
        speech_config.speech_synthesis_language = language

        # RaspberryPiのデフォルトスピーカー(ALSA経由)に出力する
        audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
        self.synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, audio_config=audio_config
        )

    def speak(self, text):
        result = self.synthesizer.speak_text_async(text).get()
        if result.reason == speechsdk.ResultReason.Canceled:
            details = speechsdk.SpeechSynthesisCancellationDetails(result)
            print(f'音声合成に失敗しました: {details.reason} {details.error_details}')
