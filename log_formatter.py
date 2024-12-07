import re
import time
from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Флаг для избежания конфликтов записи
file_lock = Lock()

def parse_log_line(line):
    # Разбор строки лога
    pattern_accept = (
        r"(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) "
        r"from (?P<ip_port>[\d.]+):\d+ accepted tcp:(?P<host>[\w.]+):(?P<port>\d+) .* "
        r"email: (?P<email>[\wА-Яа-я@.]+)"
    )
    pattern_answer = (
        r"(?P<timestamp>\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}) "
        r"localhost got answer: (?P<host>[\w.]+) -> \[(?P<ip_port>[\w\d.:]+)\] .*"
    )

    # Обработка строки ACCEPT
    if match := re.match(pattern_accept, line):
        host = match.group('host').removeprefix('www.')  # Убираем "www"
        if host == 'google.com':  # Убираем запросы к google.com
            return None
        return (
            f"[{match.group('timestamp').replace(' ', ' | ')}] "
            f"{match.group('email')}: "
            f"{match.group('ip_port')} → {host}\n"  # Убрали ACCEPT и порт IP
        )
    
    # Обработка строки ANSWER
    elif match := re.match(pattern_answer, line):
        host = match.group('host').removeprefix('www.')  # Убираем "www"
        if host == 'google.com':  # Убираем запросы к google.com
            return None
        return (
            f"[{match.group('timestamp').replace(' ', ' | ')}] "
            f"{host} → {match.group('ip_port')}\n"
        )
    
    return None

def transform_and_reverse_logs(input_file, output_file):
    with open(input_file, 'r') as infile:
        lines = infile.readlines()

    # Форматируем строки, фильтруем и переворачиваем
    reversed_lines = [parse_log_line(line) for line in reversed(lines) if parse_log_line(line)]

    # Записываем в файл с блокировкой
    with file_lock, open(output_file, 'w') as outfile:
        outfile.writelines(reversed_lines)

    print(f"Логи успешно перевёрнуты и записаны в {output_file}")

class LogFileHandler(FileSystemEventHandler):
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.last_position = 0  # Позиция последней обработки

    def on_modified(self, event):
        if event.src_path.endswith(self.input_file):
            self._process_new_lines()

    def _process_new_lines(self):
        with open(self.input_file, 'r') as infile:
            infile.seek(self.last_position)  # Пропускаем уже обработанные строки
            new_lines = infile.readlines()
            self.last_position = infile.tell()  # Обновляем позицию

        # Обрабатываем и добавляем новые строки в выходной файл
        with file_lock, open(self.output_file, 'a') as outfile:
            for line in new_lines:
                if formatted_line := parse_log_line(line):
                    outfile.write(formatted_line)

def monitor_logs(input_file, output_file):
    event_handler = LogFileHandler(input_file, output_file)
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    print(f"Запуск мониторинга файла {input_file}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    input_file = ""  # Входной файл
    output_file = ""  # Выходной файл

    # Однократная обработка файла
    transform_and_reverse_logs(input_file, output_file)
    
    # Запуск мониторинга
    monitor_logs(input_file, output_file)

