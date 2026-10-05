import datetime

# Paste your input string inside the triple quotes:
RAW_DATA = """
10:08.851 + 7:58.246 + 8:57.808 + 8:55.650 + 10:34.060 + 8:45.337 + 10:11.846 =
"""

def parse_duration(time_str: str) -> datetime.timedelta:
    """Parses timestamps in MM:SS.mmm or HH:MM:SS.mmm format."""
    parts = time_str.strip().split(":")

    if len(parts) == 3:
        hours, minutes, sec_part = int(parts[0]), int(parts[1]), parts[2]
    elif len(parts) == 2:
        hours, minutes, sec_part = 0, int(parts[0]), parts[1]
    else:
        raise ValueError(f"Invalid timestamp format: '{time_str}'")

    if "." in sec_part:
        sec_str, ms_str = sec_part.split(".")
        seconds = int(sec_str)
        # Pad or truncate milliseconds to 3 digits
        milliseconds = int(ms_str.ljust(3, "0")[:3])
    else:
        seconds = int(sec_part)
        milliseconds = 0

    return datetime.timedelta(
        hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds
    )

def sum_durations(text: str) -> datetime.timedelta:
    # Clean up '=' and '+' separators
    cleaned_text = text.replace("=", " ").replace("+", " ")
    tokens = [token.strip() for token in cleaned_text.split() if token.strip()]

    total = datetime.timedelta()
    for token in tokens:
        total += parse_duration(token)
    return total

def format_duration(td: datetime.timedelta) -> str:
    total_seconds = int(td.total_seconds())
    ms = td.microseconds // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}.{ms:03d}"
    return f"{minutes:02d}:{seconds:02d}.{ms:03d}"

if __name__ == "__main__":
    total = sum_durations(RAW_DATA)
    print(f"Total: {format_duration(total)}")
