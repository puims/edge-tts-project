import argparse
import time

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