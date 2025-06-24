from docx import Document
from secret_messege import SecretMessage, Record

ZWNJ = "\u200C"  # Zero-width non-joiner (U+200C)
MSP = "\u018E"
RTLM = "\u200F"
ZWJ = "\u200D"      

def encode_cwm(binary_str: str):
    # Проверяем, что строка содержит только 0 и 1
    if not all(c in '01' for c in binary_str):
        raise ValueError("Binary string should contain only '0' and '1'")
    
    # Дополняем биты до чётного количества (на случай стороннего использования этой функции)
    if len(binary_str) % 2 != 0:
        binary_str += '0'
    
    bit_pairs = [binary_str[i:i+2] for i in range(0, len(binary_str), 2)]
    bit_index = 0

    new_text = []
    
    while bit_index < len(bit_pairs):
        bit_pair = bit_pairs[bit_index]
        if bit_pair == '00':
            new_text.append(ZWNJ)
        elif bit_pair == '01':
            new_text.append(MSP)
        elif bit_pair == '10':
            new_text.append(RTLM)
        elif bit_pair == '11':
            new_text.append(ZWJ)
        bit_index += 1
    
    cwm = ''.join(new_text)
    return cwm

def encode_zwbsp(doc_path, binary_str: str, output_path="secret.docx"):
 
    doc = Document(doc_path)
    
    cwm = encode_cwm(binary_str)

    for paragraph in doc.paragraphs:
        for run in paragraph.runs:
        
            text = run.text
            new_text = []
            i = 0
            
            while i < len(text):
                new_text.append(text[i])
                new_text.append(cwm)
                i += 1
            
            run.text = ''.join(new_text)
    
    doc.save(output_path)
    # print(f"Бинарное сообщение внедрено в {output_path}")


def decode_zwbsp(doc_path) -> str:

    doc = Document(doc_path)
    binary_secret = []
    
    # с помощью форматной строки извлечь все цвз и посчитать сколько их

if __name__ == "__main__":

    # import random
    # random_bits = ''.join(random.choices('01', k=12))
    # records = [
    #         Record(1, random_bits)
    #     ]
    # msg = SecretMessage(records)
    msg = SecretMessage.from_binary_str("10101010000000000011010011011101101000011110111001010011000110010101001101000000000001010101")
    # print(msg)                         
    print(msg)                           
    print("Внедряемое сообщение")
    print(msg)
    binary_msg = msg.to_binary_str()
    
    encode_zwbsp("test_dataset/33.docx", binary_msg, "secret.docx")
    
    # encode_zwbsp("test.docx", binary_msg, "secret.docx")
    extracted_binary = decode_zwbsp("secret.docx")
    print(len(extracted_binary))
    
    print(extracted_binary)
    extr_msg = msg.from_binary_str(extracted_binary)
    
    print("Извлечённое сообщение")
    print(extr_msg)

    print(f"Внедрённое == извлечвенное: {msg == extr_msg}")
