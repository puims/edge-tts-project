from edge_tts import list_voices

async def get_voices(gender=None,locale=None,name=None) -> list:
    voices=await list_voices()

    if name:
        voices = [voice for voice in voices if name in voice.get("ShortName")]
        if len(voices) == 0:
            raise ValueError(f"No voices found with name containing '{name}'")
    else:
        if gender or locale:
            voices = [voice for voice in voices if
                    (gender is None or voice.get("Gender") == gender) and
                    (locale is None or voice.get("Locale") == locale)]

    return voices
