import os
from random import randint, choices
from secret_messege import SecretMessage, Record
from implementation import encode_zwbsp, decode_zwbsp
import re

def extract_number(filename):
    """Извлекает число из строки вида '...N.docx'"""
    match = re.search(r'(\d+)\.docx$', filename)
    return int(match.group(1)) if match else 0

def get_files_by_extension(folder_path, extension, rename=False):

    extension = extension.lstrip('.')
    matched_files = []
    
    for file in os.listdir(folder_path):
        if file.lower().endswith(f'.{extension.lower()}') and os.path.isfile(os.path.join(folder_path, file)):
            matched_files.append(os.path.join(folder_path, file))

    if rename:
        i = 0
        # print(matched_files)
        for file in matched_files:
            new_name = folder_path + f"/{i}." + extension
            # print(new_name)
            os.rename(file, new_name)
            matched_files[i] = new_name
            i+=1
    
    return matched_files

test_files = get_files_by_extension("./test_dataset", ".docx")
# exit()
test_files = sorted(test_files, key=extract_number)
# print(test_files)
tests_count = len(test_files)

messages = []

for i in range(tests_count):
    records = []
    records_count = randint(1, 3)
    len = 62

    for j in range(records_count):
        if len > 1:
            record_len = randint(1, len)
        else:
            record_len = 1
        len -= record_len

        rand_bin = ''.join(choices('01', k=record_len))
        records.append(Record(j+1, rand_bin))

    msg = SecretMessage(records)
    messages.append(msg)
    # print(msg)

for i in range(tests_count):
    msg = messages[i]
    file = test_files[i]

    print(f"test{i}", file)
    binary_msg = msg.to_binary_str()
    # print(msg)
    # print(binary_msg)
    
    # encode_zwbsp(file, binary_msg, f"./test_dataset_secret/secret{i}.docx")
    # extracted_binary = decode_zwbsp(f"./test_dataset_secret/secret{i}.docx")
    encode_zwbsp(file, binary_msg, "secret.docx")
    extracted_binary = decode_zwbsp("secret.docx")
    # print("extracted_binary", extracted_binary)

    # if extracted_binary == "0":
    #     print(file, " is removed")
    #     os.remove(file)
    #     continue
    try:
        extr_msg = msg.from_binary_str(extracted_binary)
    except ValueError as e:
        print(file)
        print("trying to hide message:")
        print(msg)
        print("bin form - " + binary_msg)
        print(print("extracted_binary", extracted_binary))
        print(f"{e}")

    print(f"Внедрённое == извлечвенное: {msg == extr_msg}")


