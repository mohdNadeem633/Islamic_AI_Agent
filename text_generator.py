# # import requests
# # import json
# # import random

# # def fetch_ayah():
# #     ayah = random.randint(1, 6236)

# #     ar = requests.get(
# #         f"https://api.alquran.cloud/v1/ayah/{ayah}"
# #     ).json()["data"]["text"]

# #     en = requests.get(
# #         f"https://api.alquran.cloud/v1/ayah/{ayah}/en.sahih"
# #     ).json()["data"]["text"]

# #     data = {
# #         "arabic": ar,
# #         "english": en,
# #         "reference": f"(QS. {ayah})"
# #     }

# #     with open("content/quotes.json", "w", encoding="utf-8") as f:
# #         json.dump(data, f, ensure_ascii=False, indent=2)

# #     print("✅ Quran content generated")

# # if __name__ == "__main__":
# #     fetch_ayah()

# import requests, json, random

# def fetch_random_surah():
#     surah_number = random.randint(1, 114)

#     ar = requests.get(
#         f"https://api.alquran.cloud/v1/surah/{surah_number}"
#     ).json()["data"]

#     en = requests.get(
#         f"https://api.alquran.cloud/v1/surah/{surah_number}/en.sahih"
#     ).json()["data"]

#     data = {
#         "surah_number": surah_number,
#         "surah_name_ar": ar["name"],
#         "surah_name_en": ar["englishName"],
#         "ayahs": []
#     }

#     for a, e in zip(ar["ayahs"], en["ayahs"]):
#         data["ayahs"].append({
#             "number": a["numberInSurah"],
#             "arabic": a["text"],
#             "english": e["text"]
#         })

#     with open("content/surah.json", "w", encoding="utf-8") as f:
#         json.dump(data, f, ensure_ascii=False, indent=2)

#     print(f"✅ Random Surah generated: {ar['englishName']}")

# if __name__ == "__main__":
#     fetch_random_surah()


import requests
import json
import random
import os

def fetch_random_surah():
    """
    Fetch a random Surah from the Quran API with both Arabic and English translations
    """
    # Random surah number (1-114)
    surah_number = random.randint(1, 114)
    
    print(f"[INFO] Fetching Surah #{surah_number}...")
    
    try:
        # Fetch Arabic version
        ar_response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}"
        )
        ar_response.raise_for_status()
        ar_data = ar_response.json()["data"]
        
        # Fetch English translation (Sahih International)
        en_response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/en.sahih"
        )
        en_response.raise_for_status()
        en_data = en_response.json()["data"]
        
    except requests.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    # Prepare data structure
    surah_data = {
        "surah_number": surah_number,
        "surah_name_ar": ar_data["name"],
        "surah_name_en": ar_data["englishName"],
        "revelation_type": ar_data["revelationType"],
        "number_of_ayahs": ar_data["numberOfAyahs"],
        "ayahs": []
    }
    
    # Combine Arabic and English ayahs
    for ar_ayah, en_ayah in zip(ar_data["ayahs"], en_data["ayahs"]):
        surah_data["ayahs"].append({
            "number": ar_ayah["numberInSurah"],
            "arabic": ar_ayah["text"],
            "english": en_ayah["text"]
        })
    
    # Create content directory if it doesn't exist
    os.makedirs("content", exist_ok=True)
    
    # Save to JSON file
    output_file = "content/surah.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(surah_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Surah fetched successfully!")
    print(f"   📕 Name: {ar_data['englishName']} ({ar_data['name']})")
    print(f"   📊 Type: {ar_data['revelationType']}")
    print(f"   🔢 Ayahs: {ar_data['numberOfAyahs']}")
    print(f"   💾 Saved to: {output_file}")


def fetch_specific_surah(surah_number):
    """
    Fetch a specific Surah by number
    """
    if not 1 <= surah_number <= 114:
        print("❌ Invalid surah number. Please use 1-114")
        return
    
    print(f"📖 Fetching Surah #{surah_number}...")
    
    try:
        ar_response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}"
        )
        ar_response.raise_for_status()
        ar_data = ar_response.json()["data"]
        
        en_response = requests.get(
            f"https://api.alquran.cloud/v1/surah/{surah_number}/en.sahih"
        )
        en_response.raise_for_status()
        en_data = en_response.json()["data"]
        
    except requests.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return
    
    surah_data = {
        "surah_number": surah_number,
        "surah_name_ar": ar_data["name"],
        "surah_name_en": ar_data["englishName"],
        "revelation_type": ar_data["revelationType"],
        "number_of_ayahs": ar_data["numberOfAyahs"],
        "ayahs": []
    }
    
    for ar_ayah, en_ayah in zip(ar_data["ayahs"], en_data["ayahs"]):
        surah_data["ayahs"].append({
            "number": ar_ayah["numberInSurah"],
            "arabic": ar_ayah["text"],
            "english": en_ayah["text"]
        })
    
    os.makedirs("content", exist_ok=True)
    
    output_file = "content/surah.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(surah_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Surah fetched successfully!")
    print(f"   📕 Name: {ar_data['englishName']} ({ar_data['name']})")
    print(f"   📊 Type: {ar_data['revelationType']}")
    print(f"   🔢 Ayahs: {ar_data['numberOfAyahs']}")
    print(f"   💾 Saved to: {output_file}")


if __name__ == "__main__":
    import sys
    
    # Allow command line argument for specific surah
    if len(sys.argv) > 1:
        try:
            surah_num = int(sys.argv[1])
            fetch_specific_surah(surah_num)
        except ValueError:
            print("❌ Please provide a valid number")
    else:
        fetch_random_surah()