#!/usr/bin/env python3

import argparse
import sys
import time

import requests


REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def measure_request(
    session: requests.Session,
    url: str,
    timeout: float,
) -> tuple[int, float]:
    start = time.perf_counter()
    size = 0

    with session.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            size += len(chunk)

    elapsed = time.perf_counter() - start

    return size, elapsed


def measure(url: str, num_requests: int, timeout: float) -> None:
    total_bytes = 0
    total_time = 0.0
    successful_requests = 0

    print(f"URL:      {url}")
    print(f"Запросов: {num_requests}")
    print("-" * 70)

    with requests.Session() as session:
        for number in range(1, num_requests + 1):
            try:
                size, elapsed = measure_request(
                    session,
                    url,
                    timeout,
                )
            except requests.RequestException as exc:
                print(f"Запрос {number:2d}: ОШИБКА — {exc}")
                continue

            size_mb = size / 1024 / 1024
            speed_mb_s = size_mb / elapsed

            total_bytes += size
            total_time += elapsed
            successful_requests += 1

            print(
                f"Запрос {number:2d}: "
                f"{size_mb:8.2f} МБ  "
                f"{elapsed:7.3f} с  "
                f"{speed_mb_s:8.2f} МБ/с"
            )

    print("-" * 70)

    if successful_requests == 0:
        print("Нет успешных запросов — скорость измерить нельзя.")
        sys.exit(1)

    total_mb = total_bytes / 1024 / 1024
    average_time = total_time / successful_requests
    average_speed = total_mb / total_time

    print(f"Успешных запросов:     {successful_requests}/{num_requests}")
    print(f"Всего скачано:         {total_mb:.2f} МБ")
    print(f"Общее время:           {total_time:.3f} с")
    print(f"Среднее время:         {average_time:.3f} с")
    print(f"Средняя скорость:      {average_speed:.2f} МБ/с")


def positive_int(value: str) -> int:
    number = int(value)

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "значение должно быть больше 0"
        )

    return number


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Замер скорости загрузки файла"
    )

    parser.add_argument(
        "url",
        help="URL файла для скачивания",
    )

    parser.add_argument(
        "-n",
        "--num",
        type=positive_int,
        default=REQUEST_COUNT,
        help="количество запросов",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=60,
        help="таймаут одного запроса в секундах",
    )

    args = parser.parse_args()

    measure(
        url=args.url,
        num_requests=args.num,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    main()
