import requests

reciters = {
    "alafasy": "Alafasy_128kbps",
    "basit":   "Abdul_Basit_Murattal_192kbps",
    "husary":  "Husary_128kbps",
}


def test_range(start_ayah=1, end_ayah=20, surah=1):
    for ay in range(start_ayah, end_ayah + 1):
        s = str(surah).zfill(3)
        a = str(ay).zfill(3)
        for tag, seg in reciters.items():
            url = f"https://everyayah.com/data/{seg}/{s}{a}.mp3"
            try:
                r = requests.get(url, timeout=10)
                print(f"{tag}\t{s}{a}\t{r.status_code}\t{len(r.content)}")
            except Exception as e:
                print(f"{tag}\t{s}{a}\tERR\t{e!r}")


if __name__ == "__main__":
    test_range(1, 20, 1)
