from docx import Document

ZERO_WIDTH_SPACE = "\u200C"  # ZWC (в данный момент это ZWJ)
NORMAL_SPACE = "\u0020"      # Обычный пробел

def encode_zwbsp(doc_path, secret_msg, output_path="secret.docx"):
    doc = Document(doc_path)
    binary_secret = ''.join(format(ord(char), '016b') for char in secret_msg)
    
    # Дополняем биты до чётного количества
    if len(binary_secret) % 2 != 0:
        binary_secret += '0'
    
    bit_pairs = [binary_secret[i:i+2] for i in range(0, len(binary_secret), 2)]
    bit_index = 0

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
            if bit_index >= len(bit_pairs):
                break
            
            text = run.text
            new_text = []
            i = 0
            
            while i < len(text):
                if text[i] == NORMAL_SPACE and bit_index < len(bit_pairs):
                    bit_pair = bit_pairs[bit_index]
                    
                    if bit_pair == '00':
                        new_space = NORMAL_SPACE
                    elif bit_pair == '01':
                        new_space = NORMAL_SPACE + ZERO_WIDTH_SPACE
                    elif bit_pair == '10':
                        new_space = ZERO_WIDTH_SPACE + NORMAL_SPACE
                    elif bit_pair == '11':
                        new_space = ZERO_WIDTH_SPACE + NORMAL_SPACE + ZERO_WIDTH_SPACE
                    
                    new_text.append(new_space)
                    bit_index += 1
                else:
                    new_text.append(text[i])
                i += 1
            
            run.text = ''.join(new_text)
    
    doc.save(output_path)
    print(f"Сообщение '{secret_msg}' внедрено в {output_path}")


def decode_zwbsp(doc_path):
    doc = Document(doc_path)
    binary_secret = []
    
    for paragraph in doc.paragraphs:
        text = paragraph.text
        i = 0
        while i < len(text):
            if text[i] == NORMAL_SPACE:
                # Проверяем символы вокруг пробела
                prev_char = text[i-1] if i > 0 else ''
                next_char = text[i+1] if i < len(text)-1 else ''
                
                if prev_char == ZERO_WIDTH_SPACE and next_char == ZERO_WIDTH_SPACE:
                    binary_secret.append('11')
                elif prev_char == ZERO_WIDTH_SPACE:
                    binary_secret.append('10')
                elif next_char == ZERO_WIDTH_SPACE:
                    binary_secret.append('01')
                else:
                    binary_secret.append('00')
                i += 1
            i += 1
    
    # Собираем биты в байты
    secret_msg = ''
    for i in range(0, len(binary_secret), 8): 
        byte = binary_secret[i:i+8]
        if len(byte) < 8:
            break
        secret_msg += chr(int(''.join(byte), 2))
    
    return secret_msg

messege = ""
encode_zwbsp("test.docx", "Karl stole corals from Clara", "secret.docx")

secret = decode_zwbsp("secret.docx")
print(f"Извлеченное раскодированное сообщение: {secret}")