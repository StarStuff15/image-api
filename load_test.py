"""Fire a bunch of requests at once and see which workers handled them."""
import asyncio
import base64
import sys
from collections import Counter

import httpx

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/image"
N = int(sys.argv[2]) if len(sys.argv) > 2 else 200

# 1x1 png
PNG = base64.b64encode(bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
    "1f15c4890000000d49444154789c6360000002000154a24f5d00000000"
    "49454e44ae426082"
)).decode()


async def main():
    async with httpx.AsyncClient(timeout=10) as client:
        tasks = [client.post(URL, json={"image": PNG}) for _ in range(N)]
        responses = await asyncio.gather(*tasks)

    statuses = Counter(r.status_code for r in responses)
    pids = Counter(r.headers.get("x-worker-pid") for r in responses)

    print(f"status codes: {dict(statuses)}")
    print(f"handled by {len(pids)} worker(s):")
    for pid, count in pids.most_common():
        print(f"  pid {pid}: {count}")


asyncio.run(main())
