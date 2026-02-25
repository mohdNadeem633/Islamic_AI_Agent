import json
s = 1
ayah_start = 1
ayah_end = 10
try:
    sd = json.load(open('content/surah.json', encoding='utf-8'))
    if sd.get('surah_number') == s:
        maxa = sd.get('number_of_ayahs')
        ayah_start = max(1, min(int(ayah_start), maxa))
        ayah_end = max(ayah_start, min(int(ayah_end), maxa))
    print(ayah_start, ayah_end)
except Exception as e:
    print('ERR', e)
