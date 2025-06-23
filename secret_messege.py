import struct
from typing import List

class Record:
    def __init__(self, record_type: int, data: bytes):
        if record_type < 0 or record_type > 255:
            raise ValueError("Record type must be 8-bit (0-255)")
        self.type = record_type
        self.len = len(data)
        self.data = data

    def to_binary_str(self) -> str:
        """Возвращает бинарную строку (последовательность 0 и 1)"""
        binary_str = ""
        # Конвертируем type (1 байт)
        binary_str += format(self.type, '08b')
        # Конвертируем len (1 байт)
        binary_str += format(self.len, '08b')
        # Конвертируем data
        for byte in self.data:
            binary_str += format(byte, '08b')
        return binary_str

    @classmethod
    def from_binary_str(cls, binary_str: str):
        """Создает Record из бинарной строки"""
        if len(binary_str) < 16:
            raise ValueError("Binary string too short for Record header")
        
        # Читаем type (первые 8 бит)
        record_type = int(binary_str[:8], 2)
        # Читаем len (следующие 8 бит)
        length = int(binary_str[8:16], 2)
        
        # Проверяем, что строка достаточно длинная
        if len(binary_str) < 16 + length*8:
            raise ValueError("Binary string too short for Record data")
            
        # Читаем data
        data_bytes = []
        for i in range(16, 16 + length*8, 8):
            byte_str = binary_str[i:i+8]
            data_bytes.append(int(byte_str, 2))
        
        return cls(record_type, bytes(data_bytes))

    def __repr__(self):
        return f"Record(type=0x{self.type:02X}, len={self.len}, data={self.data})"


class SecretMessage:
    HEADER = 0xAA
    TAIL = 0x55
    MAX_TOTAL_SIZE = 8  
    
    def __init__(self, records: List[Record]):
        self.records = records
        self._validate_size()
        self.check_summ = self.calculate_checksum()
    
    def _validate_size(self):
        """Проверяет, что суммарный размер всех records не превышает 8 байт"""
        total_size = sum(2 + record.len for record in self.records) 
        if total_size > self.MAX_TOTAL_SIZE:
            raise ValueError(f"Total size of all records exceeds 8 bytes (got {total_size} bytes")
    
    def calculate_checksum(self) -> int:
        checksum = 0
        for record in self.records:
            checksum ^= record.type
            checksum ^= record.len
            for byte in record.data:
                checksum ^= byte
        return checksum & 0xFF

    def to_binary_str(self) -> str:
        """Возвращает полное бинарное представление сообщения в виде строки из 0 и 1"""
        binary_str = format(self.HEADER, '08b')  
        
        for record in self.records:
            binary_str += record.to_binary_str()
            
        binary_str += format(self.check_summ, '08b')  
        binary_str += format(self.TAIL, '08b')       
        return binary_str

    @classmethod
    def from_binary_str(cls, binary_str: str):
        """Создает SecretMessage из бинарной строки с возможными лишними битами в конце"""
        # Минимальная длина - header (8) + checksum (8) + tail (8)
        if len(binary_str) < 24:
            raise ValueError("Binary string too short for message")
        
        # Ищем заголовок в начале
        header = int(binary_str[:8], 2)
        if header != cls.HEADER:
            raise ValueError(f"Invalid header. Expected {cls.HEADER:08b}, got {header:08b}")

        # Ищем хвост в строке (может быть не строго в конце)
        tail_pos = -1
        for i in range(len(binary_str)-8, 7, -1):  # Ищем с конца
            if int(binary_str[i:i+8], 2) == cls.TAIL:
                tail_pos = i
                break
        
        if tail_pos == -1:
            raise ValueError("Tail marker not found in binary string")

        # Контрольная сумма должна быть за 8 бит до хвоста
        if tail_pos - 8 < 8:  # 8 - минимальная позиция после header
            raise ValueError("Invalid message format: checksum before header")

        check_summ = int(binary_str[tail_pos-8:tail_pos], 2)
        
        # Обрабатываем записи между header и checksum
        records_data = binary_str[8:tail_pos-8]
        records = []
        i = 0
        while i < len(records_data):
            if i + 16 > len(records_data):
                # Неполная запись - возможно, лишние биты в конце
                break
                    
            # Читаем длину данных записи
            record_len = int(records_data[i+8:i+16], 2)
            
            # Проверяем, что есть место для данных
            if i + 16 + record_len*8 > len(records_data):
                # Не хватает данных для полной записи - пропускаем
                break
                
            # Извлекаем полную запись
            record_end = i + 16 + record_len*8
            record_binary = records_data[i:record_end]
            try:
                records.append(Record.from_binary_str(record_binary))
            except ValueError:
                # Ошибка в формате записи - возможно, поврежденные данные
                break
                
            i = record_end
        
        # Создаем сообщение и проверяем контрольную сумму
        message = cls(records)
        if message.check_summ != check_summ:
            raise ValueError(f"Checksum mismatch. Calculated {message.check_summ:08b}, got {check_summ:08b}")
            
        return message

    def __repr__(self):
        records_str = ",\n    ".join(str(r) for r in self.records)
        return (f"SecretMessage(\n"
                f"  header=0x{self.HEADER:02X},\n"
                f"  records=[{records_str}],\n"
                f"  check_summ=0x{self.check_summ:02X},\n"
                f"  tail=0x{self.TAIL:02X}\n"
                f")")