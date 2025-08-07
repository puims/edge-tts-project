
def text_handler(text)->str:
    pattern = '：，。？！】'
    for ch in text:
        if ch in pattern:
            text = text.replace(ch,'\n')
        elif ch == '…' or ch == '【':
            text = text.replace(ch,'')

    with open('output.srt','w',encoding='utf-8') as f:
        f.write(text)
    
def get_text(path)->str:
    with open(path, 'r', encoding='utf-8') as file:
        text = file.read().strip()

    return text