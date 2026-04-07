from __future__ import annotations

from telemetry import export_chrome_trace


if __name__ == "__main__":
    output_path = export_chrome_trace()
    print(output_path)
