
from datetime import date

GOVERNORATES = {
    "01": "Cairo",
    "02": "Alexandria",
    "03": "Port Said",
    "04": "Suez",
    "11": "Damietta",
    "12": "Dakahlia",
    "13": "Sharqia",
    "14": "Qalyubia",
    "15": "Kafr El Sheikh",
    "16": "Gharbia",
    "17": "Monufia",
    "18": "Beheira",
    "19": "Ismailia",
    "21": "Giza",
    "22": "Beni Suef",
    "23": "Fayoum",
    "24": "Minya",
    "25": "Asyut",
    "26": "Sohag",
    "27": "Qena",
    "28": "Aswan",
    "29": "Luxor",
    "31": "Red Sea",
    "32": "New Valley",
    "33": "Matrouh",
    "34": "North Sinai",
    "35": "South Sinai",
    "88": "Born Abroad"
}

GOVERNORATES_AR = {
    "01": "القاهرة",
    "02": "الإسكندرية",
    "03": "بورسعيد",
    "04": "السويس",
    "11": "دمياط",
    "12": "الدقهلية",
    "13": "الشرقية",
    "14": "القليوبية",
    "15": "كفر الشيخ",
    "16": "الغربية",
    "17": "المنوفية",
    "18": "البحيرة",
    "19": "الإسماعيلية",
    "21": "الجيزة",
    "22": "بني سويف",
    "23": "الفيوم",
    "24": "المنيا",
    "25": "أسيوط",
    "26": "سوهاج",
    "27": "قنا",
    "28": "أسوان",
    "29": "الأقصر",
    "31": "البحر الأحمر",
    "32": "الوادي الجديد",
    "33": "مطروح",
    "34": "شمال سيناء",
    "35": "جنوب سيناء",
    "88": "مولود خارج مصر",
}


def validate_national_id(national_id: str) -> tuple[bool, str]:

    national_id = str(national_id)

    if len(national_id) != 14: #validate the length of the entered national ID
        return False, "National ID must contain 14 digits."

    if not national_id.isascii() or not national_id.isdigit(): #make sure that the national ID is in english digits only 
        return False, "National ID must have English digits only."

    century = national_id[0] #first index of the ID is the century the person was born in

    if century == "2":
        birth_century = 1900
    elif century == "3":
        birth_century = 2000
    else:
        return False, "Invalid century."

    year = int(national_id[1:3]) + birth_century #adding birth_century to get correct format ex:2001 not 1
    month = int(national_id[3:5])
    day = int(national_id[5:7])

    try:
        birth_date = date(year, month, day)
    except ValueError:
        return False, "Invalid date of birth in National ID."

    if birth_date > date.today():
        return False, "Date of birth cannot be in the future."

    gov_code = national_id[7:9]

    if gov_code not in GOVERNORATES: #governorate code has to be valid by being in dictionary GOVERNORATES
        return False, "Invalid governorate code."

    return True, "Valid National ID format."


def extract_id_data(national_id: str) -> dict[str, str] | None:

    is_valid, message = validate_national_id(national_id)

    if not is_valid:
        return None

    national_id = str(national_id)

    century = national_id[0]

    if century == "2":
        birth_century = 1900
    else:
        birth_century = 2000

    year = int(national_id[1:3]) + birth_century
    month = int(national_id[3:5])
    day = int(national_id[5:7])

    gov_code = national_id[7:9]
    governorate = GOVERNORATES[gov_code]

    birth_date = date(year, month, day)

    return { #return extacted info as dictionary 
        "date_of_birth": birth_date.strftime("%Y-%m-%d"),
        "governorate_code": gov_code,
        "governorate": governorate
    }


def get_governorate_names(governorate_code: str) -> dict[str, str] | None:
    """Return the Arabic and English names for a validated governorate code."""
    if governorate_code not in GOVERNORATES:
        return None
    return {
        "ar": GOVERNORATES_AR[governorate_code],
        "en": GOVERNORATES[governorate_code],
    }


if __name__ == "__main__":  # بيشتغل لما تشغّل الملف مباشرة بس، مش وقت الـ import
    national_id = input("Enter your National ID: ") #get user input

    valid, message = validate_national_id(national_id) #call validation function

    print(message) #displays message returned by validate_national_id function 

    if valid:
        data = extract_id_data(national_id) #calls extract_id_data() to extract info from the ID.
        print(data) #prints the dictionary
