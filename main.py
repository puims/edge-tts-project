import asyncio
import random

from edge_tts import Communicate

from pkg.args import parse_args
from pkg.text import get_text,text_handler
from pkg.voices import get_voices

async def main() -> None:
    """Main function"""
    args= parse_args()
    if args.command == 'actors':
        voices = await get_voices(gender=args.gender, locale=args.language,name=args.name)
        for v in voices:
            print(f"Name: {v["ShortName"]},")
        return

    text = get_text(args.input)
    text_handler(text)
    
    voices=await get_voices(args.gender,args.language,args.name)
    if args.name:
        voice = voices[0]["Name"]
    else:
        voice = random.choice(voices)["Name"]

    communicate = Communicate(text=text, voice=voice, rate=args.rate, volume=args.volume, pitch=args.pitch)

    with open(args.output, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
    
    print(f'voice name: {voice}\n')

if __name__ == "__main__":
    asyncio.run(main())