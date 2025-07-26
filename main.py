import argparse
import asyncio
import random
import re
import time

from edge_tts import Communicate, SubMaker,list_voices

def get_text(path) -> str:
    """Get the text to be converted to speech"""
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().strip()
    if not text:
        raise ValueError("Input text file is empty.")
    return text

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Text-to-Speech with Edge TTS")
    sub_parser = parser.add_subparsers(dest='command', required=False)

    parser.add_argument('-l', '--language', type=str,default='zh-CN', help='Language code for the voice (e.g., "zh-CN")')
    parser.add_argument('-g', '--gender', type=str, default='Female')
    parser.add_argument('-i', '--input', type=str, default='text', help='Input text file')
    parser.add_argument('-n', '--name', type=str, default=None, help='Voice name (optional)')
    parser.add_argument('-r', '--rate', type=int, default=0, help='Speech rate (e.g., "0%", "10%", "-10%")')
    parser.add_argument('-v', '--volume', type=int, default=0, help='Speech volume (e.g., "0%", "10%", "-10%")')
    parser.add_argument('-p', '--pitch', type=int, default=0, help='Speech pitch (e.g., "0%", "10%", "-10%")')
    # parser.add_argument('-o', '--output', type=str, default='output.mp3', help='Output audio file name')
    parser.add_argument('-o', '--output', type=str, default=f'{int(time.time())}.mp3', help='Output audio file name')

    actors = sub_parser.add_parser('actors', help='List available voices')
    actors.add_argument('-l', '--language', type=str, default='zh-CN', help='Filter voices by language')
    actors.add_argument('-g','--gender', type=str, default='Female', help='Filter voices by gender')

    args = parser.parse_args()

    if args.name:
        args.name = args.name.lower()
        args.name = args.name.capitalize()
    args.gender = args.gender.lower()
    args.gender = args.gender.capitalize()

    if args.rate<0:
        args.rate = f"{args.rate}%"
    elif args.rate>=0:
        args.rate = f"+{args.rate}%"

    if args.volume<0:
        args.volume = f"{args.volume}%"
    elif args.volume>=0:
        args.volume = f"+{args.volume}%"

    if args.pitch<0:
        args.pitch = f"{args.pitch}Hz"
    elif args.pitch>=0:
        args.pitch = f"+{args.pitch}Hz"
    # else:
    #     args.pitch = "0Hz"

    return args

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

def merge_word_boundaries(word_boundaries, max_len=15):
    """
    合并WordBoundary为句子，遇到除空格外的标点或\n或达到最大长度时分句，英文单词间空格保留
    """
    srt_blocks = []
    current = []
    for i, word in enumerate(word_boundaries):
        current.append(word)
        text = word['text']
        # 判断是否为分句标点（排除空格），或遇到换行，或达到最大长度，或最后一个词
        if (re.match(r'[^\w\s]', text) and text != ' ') or text == '\n' or len(current) >= max_len or i == len(word_boundaries) - 1:
            start = current[0]['offset']
            end = current[-1]['offset'] + current[-1]['duration']
            # 保留英文单词间空格
            sentence = ''
            for w in current:
                if w['text'] == ' ':
                    sentence += ' '
                else:
                    sentence += w['text']
            # 去除句首句尾空格和换行
            sentence = sentence.strip().replace('\n', '')
            if sentence:  # 避免空句
                srt_blocks.append((start, end, sentence))
            current = []
    return srt_blocks

async def main() -> None:
    """Main function"""
    args= parse_args()
    if args.command == 'actors':
        voices = await get_voices(gender=args.gender, locale=args.language,name=args.name)
        for v in voices:
            print(f"Name: {v["ShortName"]},")
        return

    text = get_text(args.input)
    voices=await get_voices(args.gender,args.language,args.name)
    if args.name:
        voice = voices[0]["Name"]
    else:
        voice = random.choice(voices)["Name"]

    communicate = Communicate(text=text, voice=voice, rate=args.rate, volume=args.volume, pitch=args.pitch)
    # submaker = SubMaker()
    word_boundaries = []

    with open(args.output, "wb") as file:
        async for chunk in communicate.stream():
            # Check if the chunk is audio or a word boundary
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                word_boundaries.append(chunk)

    srt_blocks = merge_word_boundaries(word_boundaries)
    def format_srt_time(ms):
        s = int(ms // 1000)
        ms = int(ms % 1000)
        m = s // 60
        s = s % 60
        h = m // 60
        m = m % 60
        return f"{h:02}:{m:02}:{s:02},{ms:03}"
    
    with open("output.srt", "w", encoding="utf-8") as file:
        for i,(start, end, text) in enumerate(srt_blocks,1):
            file.write(f'{i}\n{format_srt_time(start)} --> {format_srt_time(end)}\n{text}\n\n')
    
    print(f'voice name: {voice}\n')

if __name__ == "__main__":
    asyncio.run(main())