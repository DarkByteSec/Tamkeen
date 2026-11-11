"""
TAMKEEN 🎓 — ui.py  (Person 5: Streamlit UI)

الواجهة بس. أي منطق (فلترة، تحقق، تقرير) بيتنادى من باقي الملفات.

=====================  CONTRACT (متفق عليه مع الفريق؟ راجعوه)  =====================
services.py
    filter_services(disability_key: str) -> list[dict]
    كل service dict فيه:
        id, name_ar, name_en, authority_ar, authority_en,
        description_ar, description_en,
        eligibility_ar (list[str]), eligibility_en (list[str]),
        documents: [{"id": "...", "name_ar": "...", "name_en": "..."}],
        official_url, in_person (bool), source, last_reviewed ("YYYY-MM-DD")
    (لو الداتا مش ثنائية اللغة الواجهة بترجع للحقل بدون _ar/_en)

checklist.py
    check_documents(required_docs: list[dict], available_ids: list[str]) -> dict
        {"percent": float 0-100, "missing": [doc_id, ...]}

validators.py
    validate_national_id(nid: str) -> {"valid": bool, "error": str | None}
        error codes المتوقعة: "length" | "digits" | "century" | "date"
    extract_national_id_data(nid: str) -> {"birth_date": "YYYY-MM-DD",
                                           "governorate": str | None,
                                           "gender": str | None}

report_generator.py
    generate_report(data: dict) -> str   # مسار ملف TXT
        data: service, authority, user_data, docs_have, docs_missing,
              next_steps, official_url, in_person, lang, generated_at

الواجهة تستخدم DEMO للخدمات وقائمة المستندات والتحقق عند غياب وحداتها الاختيارية.
report_generator.py مطلوب لعرض صفحة الملخص وإنشاء التقرير.
=====================================================================================
"""

import json
from datetime import datetime
from pathlib import Path

import streamlit as st
from report_generator import build_report_text, generate_report, render_summary_page

# ----------------------------------------------------------------------------------
# Optional imports من باقي الـ modules
# ----------------------------------------------------------------------------------
try:
    import services as services_mod
except ImportError:
    services_mod = None
try:
    import checklist as checklist_mod
except ImportError:
    checklist_mod = None
try:
    import validators as validators_mod
except ImportError:
    validators_mod = None


PROGRESS_FILE = Path("data/progress.json")

# أيقونة التاب: إيموجي 🎓 بدقة عالية (128px) مدمجة هنا عشان مفيش ملف إضافي
APP_ICON_B64 = (
    "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"
)


def app_icon():
    """بترجّع صورة الأيقونة، ولو فشلت بترجع للإيموجي 🎓."""
    try:
        import base64
        import io
        from PIL import Image
        return Image.open(io.BytesIO(base64.b64decode(APP_ICON_B64)))
    except (ImportError, OSError, ValueError):
        return "🎓"

# ----------------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------------
# المفاتيح لازم تتطابق مع "disability_types" في services.json
DISABILITY_TYPES = [
    ("visual", "👁️", "إعاقة بصرية", "Visual disability"),
    ("hearing", "👂", "إعاقة سمعية", "Hearing disability"),
    ("mobility", "🦽", "إعاقة حركية", "Mobility disability"),
    ("intellectual", "🧠", "إعاقة ذهنية", "Intellectual disability"),
]

PAGES = ["home", "services", "checklist", "national_id", "summary"]

TEXTS = {
    "ar": {
        "lang_btn": "English 🌐",
        "no_docs": "قائمة المستندات المطلوبة لسه مش متسجلة للخدمة دي. راجع الجهة المسؤولة قبل ما تقدّم.",
        "no_url": "الرابط الرسمي للخدمة دي لسه مش متسجل.",
        "menu": "☰ القائمة",
        "menu_close": "✕ إغلاق القائمة",
        "tagline": "اعرف حقوقك وجهّز أوراقك قبل ما تقدّم",
        "nav_home": "١. نوع الإعاقة",
        "nav_services": "٢. الخدمات",
        "nav_checklist": "٣. المستندات",
        "nav_national_id": "٤. الرقم القومي",
        "nav_summary": "٥. الملخص والتقديم",
        "hero_title": "أهلاً بيك في تمكين 👋",
        "hero_text": "اختار نوع الإعاقة أو احتياجك، وهنعرضلك الخدمات الحكومية المتاحة ليك بس، "
                     "ونساعدك تجهّز أوراقك عشان طلبك ما يترفضش بسبب نقص أو غلطة.",
        "choose_type": "اختار نوع الإعاقة",
        "services_title": "الخدمات المتاحة ليك",
        "no_type": "اختار نوع الإعاقة الأول من الصفحة الأولى.",
        "no_services": "مفيش خدمات متسجلة لحد دلوقتي للنوع ده.",
        "authority": "الجهة المسؤولة",
        "eligibility": "شروط الاستحقاق",
        "source": "المصدر",
        "last_reviewed": "آخر مراجعة",
        "choose": "اختار الخدمة دي",
        "selected": "الخدمة المختارة",
        "checklist_title": "قائمة المستندات",
        "checklist_hint": "علّم على الأوراق اللي معاك فعلاً.",
        "generic_docs_notice": "القائمة دي عامة ومعلوماتية فقط، ومش تأكيد رسمي لمتطلبات الخدمة. راجع الجهة المسؤولة.",
        "no_service": "اختار خدمة الأول من صفحة الخدمات.",
        "ready": "جاهز",
        "missing_docs": "مستندات ناقصة",
        "missing_warn": "لسه ناقصك الأوراق دي، يفضل تجهّزها قبل ما تروح أو تقدّم:",
        "all_ready": "كل المستندات جاهزة 🎉",
        "id_title": "فحص الرقم القومي",
        "id_hint": "اكتب الرقم القومي (14 رقم) عشان نراجع تنسيقه ونستخرج البيانات.",
        "id_input": "الرقم القومي",
        "id_check": "تحقق",
        "id_valid": "التنسيق سليم ✅",
        "birth_date": "تاريخ الميلاد",
        "governorate": "المحافظة",
        "gender": "النوع",
        "unknown_gov": "غير معروف",
        "id_disclaimer": "⚠️ التحقق بيراجع التنسيق بس. ده مش بيثبت إن الرقم حقيقي "
                         "أو إن بيانات صاحبه صحيحة.",
        "id_consent": "أوافق على إدراج تاريخ الميلاد والمحافظة في الملخص (من غير الرقم القومي)",
        "err_length": "الرقم لازم يكون 14 رقم بالظبط.",
        "err_digits": "الرقم لازم يتكوّن من أرقام فقط.",
        "err_century": "أول رقم في الرقم القومي غير صحيح.",
        "err_date": "تاريخ الميلاد داخل الرقم غير منطقي.",
        "err_future": "تاريخ الميلاد داخل الرقم في المستقبل.",
        "err_gov": "كود المحافظة داخل الرقم غير معروف.",
        "male": "ذكر",
        "female": "أنثى",
        "summary_title": "ملخص الطلب والتقديم",
        "gen_report": "إنشاء ملخص TXT 📄",
        "download": "تحميل الملخص ⬇️",
        "report_ready": "تم إنشاء الملخص.",
        "report_error": "تعذر إنشاء ملف الملخص. تحقق من صلاحيات مجلد التقارير.",
        "portal_title": "صفحة التقديم الرسمية",
        "open_portal": "افتح صفحة الخدمة الرسمية",
        "in_person": "التقديم على الخدمة دي بيتم حضورياً.",
        "last_step": "آخر خطوة قبل الانتقال: راجع الملخص وتأكد إن الأوراق جاهزة.",
        "portal_disclaimer": "تمكين مش بيقدّم الطلب نيابة عنك، وقبول الطلب مش مضمون.",
        "step1": "راجع بياناتك والأوراق المطلوبة.",
        "step2": "جهّز الأصول والصور حسب القائمة.",
        "step3": "افتح صفحة الخدمة الرسمية أو روح للجهة المسؤولة.",
        "progress": "تقدّمك",
        "st_done": "مكتملة",
        "st_missing": "ناقصة",
        "st_review": "تحتاج مراجعة",
        "p_service": "اختيار الخدمة",
        "p_docs": "المستندات",
        "p_id": "فحص الرقم القومي",
        "p_report": "الملخص",
        "save": "حفظ التقدم 💾",
        "load": "استكمال التقدم 📂",
        "saved": "تم حفظ التقدم.",
        "loaded": "تم استرجاع التقدم.",
        "no_saved": "مفيش تقدّم محفوظ.",
        "next": "التالي ←",
        "back": "→ رجوع",
        "demo_note": "⚙️ وضع تجريبي: بعض الملفات لسه ما اتربطتش.",
        "load_error": "تعذر تحميل بيانات الخدمات. راجع ملف البيانات وحاول مرة أخرى.",
    },
    "en": {
        "lang_btn": "عربي 🌐",
        "no_docs": "The required documents for this service aren't listed yet. Check with the responsible authority before you apply.",
        "no_url": "The official link for this service isn't listed yet.",
        "menu": "☰ Menu",
        "menu_close": "✕ Close menu",
        "tagline": "Know your rights and get your papers ready before you apply",
        "nav_home": "1. Disability",
        "nav_services": "2. Services",
        "nav_checklist": "3. Documents",
        "nav_national_id": "4. National ID",
        "nav_summary": "5. Summary & Apply",
        "hero_title": "Welcome to TAMKEEN 👋",
        "hero_text": "Pick your disability type or need and we'll show only the government "
                     "services available to you, then help you prepare your papers so your "
                     "request isn't rejected over a missing document or a typo.",
        "choose_type": "Choose your disability type",
        "services_title": "Services available to you",
        "no_type": "Please choose a disability type on the first page.",
        "no_services": "No services are listed yet for this type.",
        "authority": "Responsible authority",
        "eligibility": "Eligibility conditions",
        "source": "Source",
        "last_reviewed": "Last reviewed",
        "choose": "Choose this service",
        "selected": "Selected service",
        "checklist_title": "Document checklist",
        "checklist_hint": "Tick the documents you already have.",
        "generic_docs_notice": "This is a general informational checklist, not official confirmation of this service's requirements. Check with the responsible authority.",
        "no_service": "Please choose a service first.",
        "ready": "Ready",
        "missing_docs": "Missing documents",
        "missing_warn": "You're still missing these. Better to prepare them before you go or apply:",
        "all_ready": "All documents are ready 🎉",
        "id_title": "National ID check",
        "id_hint": "Enter your 14-digit national ID so we can check its format and extract data.",
        "id_input": "National ID",
        "id_check": "Validate",
        "id_valid": "Format looks valid ✅",
        "birth_date": "Birth date",
        "governorate": "Governorate",
        "gender": "Gender",
        "unknown_gov": "Unknown",
        "id_disclaimer": "⚠️ Validation only checks the format. It does not prove the number "
                         "is real or that its owner's data is correct.",
        "id_consent": "I agree to include my birth date and governorate in the summary (not my National ID)",
        "err_length": "The number must be exactly 14 digits.",
        "err_digits": "The number must contain digits only.",
        "err_century": "The first digit of the national ID is invalid.",
        "err_date": "The birth date inside the number is not valid.",
        "err_future": "The birth date inside the number is in the future.",
        "err_gov": "The governorate code inside the number is unknown.",
        "male": "Male",
        "female": "Female",
        "summary_title": "Application summary & apply",
        "gen_report": "Generate TXT summary 📄",
        "download": "Download summary ⬇️",
        "report_ready": "Summary created.",
        "report_error": "Could not create the summary file. Check the reports folder permissions.",
        "portal_title": "Official application page",
        "open_portal": "Open the official service page",
        "in_person": "This service is applied for in person.",
        "last_step": "Last step before you go: review the summary and make sure your papers are ready.",
        "portal_disclaimer": "TAMKEEN does not submit anything on your behalf, and acceptance is not guaranteed.",
        "step1": "Review your data and required documents.",
        "step2": "Prepare originals and copies as listed.",
        "step3": "Open the official service page or visit the responsible authority.",
        "progress": "Your progress",
        "st_done": "Done",
        "st_missing": "Missing",
        "st_review": "Needs review",
        "p_service": "Service chosen",
        "p_docs": "Documents",
        "p_id": "National ID check",
        "p_report": "Summary",
        "save": "Save progress 💾",
        "load": "Resume progress 📂",
        "saved": "Progress saved.",
        "loaded": "Progress restored.",
        "no_saved": "No saved progress.",
        "next": "Next →",
        "back": "← Back",
        "demo_note": "⚙️ Demo mode: some modules are not connected yet.",
        "load_error": "Could not load service data. Check the data file and try again.",
    },
}

# ----------------------------------------------------------------------------------
# DEMO fallbacks  (تتمسح بعد ما باقي الملفات تتدمج)
# بيانات تجريبية بس، مش معلومات رسمية.
# ----------------------------------------------------------------------------------
DEMO_SERVICES = [
    {
        "id": "demo_1",
        "name_ar": "خدمة تجريبية ١",
        "name_en": "Demo service 1",
        "authority_ar": "جهة تجريبية",
        "authority_en": "Demo authority",
        "description_ar": "وصف تجريبي للخدمة لحد ما بيانات services.json توصل.",
        "description_en": "Placeholder description until services.json arrives.",
        "eligibility_ar": ["شرط تجريبي ١", "شرط تجريبي ٢"],
        "eligibility_en": ["Demo condition 1", "Demo condition 2"],
        "documents": [
            {"id": "d1", "name_ar": "مستند تجريبي ١", "name_en": "Demo document 1"},
            {"id": "d2", "name_ar": "مستند تجريبي ٢", "name_en": "Demo document 2"},
            {"id": "d3", "name_ar": "مستند تجريبي ٣", "name_en": "Demo document 3"},
        ],
        "official_url": "https://example.com",
        "in_person": True,
        "source": "DEMO",
        "last_reviewed": "2026-10-24",
        "disability_types": ["visual", "hearing", "mobility", "intellectual"],
    }
]

_DEMO_GOV = {
    "01": {"ar": "القاهرة", "en": "Cairo"},
    "02": {"ar": "الإسكندرية", "en": "Alexandria"},
    "21": {"ar": "الجيزة", "en": "Giza"},
}


def _demo_validate(nid):
    if not nid.isdigit():
        return {"valid": False, "error": "digits"}
    if len(nid) != 14:
        return {"valid": False, "error": "length"}
    if nid[0] not in "23":
        return {"valid": False, "error": "century"}
    try:
        _demo_birth(nid)
    except ValueError:
        return {"valid": False, "error": "date"}
    return {"valid": True, "error": None}


def _demo_birth(nid):
    century = 1900 if nid[0] == "2" else 2000
    return datetime(century + int(nid[1:3]), int(nid[3:5]), int(nid[5:7]))


def _demo_extract(nid):
    return {
        "birth_date": _demo_birth(nid).strftime("%Y-%m-%d"),
        "governorate": _DEMO_GOV.get(nid[7:9]),
        "gender": "male" if int(nid[12]) % 2 else "female",
    }


# ----------------------------------------------------------------------------------
# Adapters: بيكلموا الـ modules الحقيقية أو الـ DEMO
# ----------------------------------------------------------------------------------
def demo_mode():
    return not all([services_mod, checklist_mod, validators_mod])


# مفاتيح الواجهة -> التصنيف العربي المستخدم في services.json (target_disabilities)
DISABILITY_AR = {
    "visual": "بصرية",
    "hearing": "سمعية",
    "mobility": "حركية",
    "intellectual": "ذهنية",
}


def _bi(value):
    """يرجّع (ar, en) من dict {"ar": .., "en": ..} أو من نص عادي."""
    if isinstance(value, dict):
        ar = value.get("ar", "")
        return ar, value.get("en", ar)
    return (value or ""), (value or "")


def _services_from_manager(disability_key):
    """
    بيكلّم ServiceManager بتاع services.py. الفلترة منه هو، والواجهة بس بتحوّل الشكل:
    - بتنادي اللغتين وتدمجهم عشان زرار عربي/English.
    - الحقول الإضافية (authority, documents, official_url, in_person, source,
      last_reviewed) بتتقرا من الـ JSON الخام لو موجودة، ومفيش حاجة بتتألّف لو ناقصة.
    """
    manager = services_mod.ServiceManager()
    category = DISABILITY_AR.get(disability_key)
    ar_items = manager.getFilteredServices("ar", category)
    en_by_id = {i["service_id"]: i for i in manager.getFilteredServices("en", category)}
    raw_by_id = {r.get("service_id"): r for r in manager.loadServicesData()}

    result = []
    for a in ar_items:
        sid = a["service_id"]
        e = en_by_id.get(sid, a)
        raw = raw_by_id.get(sid, {})
        auth_ar, auth_en = _bi(raw.get("authority"))
        docs = []
        for d in raw.get("documents", []) or []:
            name_ar, name_en = _bi(d.get("name"))
            docs.append({"id": str(d.get("id")), "name_ar": name_ar, "name_en": name_en})
        result.append({
            "id": str(sid),
            "name_ar": a["service_name"], "name_en": e["service_name"],
            "description_ar": a["description"], "description_en": e["description"],
            "eligibility_ar": [a["requirements"]] if a.get("requirements") else [],
            "eligibility_en": [e["requirements"]] if e.get("requirements") else [],
            "authority_ar": auth_ar, "authority_en": auth_en,
            "documents": docs,
            "official_url": raw.get("official_url", ""),
            "in_person": bool(raw.get("in_person", False)),
            "source": raw.get("source", ""),
            "last_reviewed": raw.get("last_reviewed", ""),
        })
    return result


# قايمة مستندات عامة مبدئية: بتظهر بس للخدمات اللي مفيهاش مستندات خاصة في services.json.
# (نفس الأربع مستندات اللي في مثال checklist.py). مش قايمة رسمية، والواجهة بتنبّه المستخدم.
DEFAULT_DOCUMENTS = [
    {"id": "id_copy", "name_ar": "صورة بطاقة الرقم القومي", "name_en": "National ID copy"},
    {"id": "medical_report", "name_ar": "تقرير طبي", "name_en": "Medical report"},
    {"id": "photo", "name_ar": "صورة شخصية", "name_en": "Personal photo"},
    {"id": "residence_proof", "name_ar": "إثبات محل الإقامة", "name_en": "Proof of residence"},
]


def _with_default_docs(services):
    for svc in services:
        if not svc.get("documents"):
            svc["documents"] = [dict(d) for d in DEFAULT_DOCUMENTS]
            svc["docs_generic"] = True
    return services


def get_services(disability_key):
    if services_mod and hasattr(services_mod, "filter_services"):
        return _with_default_docs(services_mod.filter_services(disability_key))
    if services_mod and hasattr(services_mod, "ServiceManager"):
        return _with_default_docs(_services_from_manager(disability_key))
    return [s for s in DEMO_SERVICES if disability_key in s["disability_types"]]


def get_checklist(required_docs, have_ids):
    if checklist_mod and hasattr(checklist_mod, "check_documents"):
        return checklist_mod.check_documents(required_docs, have_ids)
    if checklist_mod and hasattr(checklist_mod, "evaluate_checklist"):
        # checklist.py بتشتغل بأسماء المستندات (نصوص) وقاموس {الاسم: متوفر؟}
        # فبنحوّل الـ ids لأسماء باللغة الحالية، وبعدين نرجّع الناقص كـ ids.
        names = {d["id"]: fld(d, "name") for d in required_docs}
        choices = {name: (doc_id in have_ids) for doc_id, name in names.items()}
        res = checklist_mod.evaluate_checklist(list(names.values()), choices)
        missing_names = set(res["missing_documents"])
        return {
            "percent": res["completion_percentage"],
            "missing": [doc_id for doc_id, name in names.items() if name in missing_names],
        }
    missing = [d["id"] for d in required_docs if d["id"] not in have_ids]
    total = len(required_docs)
    percent = 100.0 if total == 0 else (total - len(missing)) / total * 100
    return {"percent": percent, "missing": missing}


# رسائل validators.py (إنجليزي) -> أكواد الأخطاء اللي الواجهة بتترجمها
_ID_ERROR_CODES = {
    "National ID must contain 14 digits.": "length",
    "National ID must have English digits only.": "digits",
    "Invalid century.": "century",
    "Invalid date of birth in National ID.": "date",
    "Date of birth cannot be in the future.": "future",
    "Invalid governorate code.": "gov",
}


def validate_id(nid):
    """بيقبل الشكلين: dict {"valid","error"} أو tuple (ok, message)."""
    if not validators_mod:
        return _demo_validate(nid)
    res = validators_mod.validate_national_id(nid)
    if isinstance(res, tuple):
        ok, msg = res
        return {"valid": bool(ok), "error": None if ok else _ID_ERROR_CODES.get(msg, msg)}
    return res


def extract_id(nid):
    """بيقبل أسماء الدوال والمفاتيح بتاعت الشخص التالت أو اللي في الـ CONTRACT."""
    if not validators_mod:
        return _demo_extract(nid)
    fn = (getattr(validators_mod, "extract_national_id_data", None)
          or getattr(validators_mod, "extract_id_data"))
    res = fn(nid) or {}
    governorate = res.get("governorate")
    governorate_code = res.get("governorate_code") or nid[7:9]
    get_names = getattr(validators_mod, "get_governorate_names", None)
    if get_names:
        governorate = get_names(governorate_code) or governorate
    return {
        "birth_date": res.get("birth_date") or res.get("date_of_birth"),
        "governorate": governorate,
        "gender": res.get("gender"),             # اختياري
    }


def make_report(data):
    return generate_report(data)


_REPORT_LABELS = {
    "ar": {
        "title": "TAMKEEN - ملخص الطلب",
        "date": "تاريخ الإنشاء", "service": "الخدمة", "authority": "الجهة المسؤولة",
        "user": "بيانات المستخدم", "no_user": "لم يتم إدراج بيانات",
        "national_id": "الرقم القومي", "birth_date": "تاريخ الميلاد", "governorate": "المحافظة",
        "have": "المستندات المتوفرة", "missing": "المستندات الناقصة", "none": "لا يوجد",
        "steps": "الخطوات التالية", "portal": "صفحة الخدمة الرسمية",
        "in_person": "ملحوظة: التقديم على هذه الخدمة يتم حضورياً.",
        "disclaimer": "تنبيه: تمكين لا يقدّم الطلب نيابة عنك، وقبول الطلب غير مضمون.",
    },
    "en": {
        "title": "TAMKEEN - Application summary",
        "date": "Generated", "service": "Service", "authority": "Responsible authority",
        "user": "User data", "no_user": "No data included",
        "national_id": "National ID", "birth_date": "Birth date", "governorate": "Governorate",
        "have": "Documents available", "missing": "Missing documents", "none": "None",
        "steps": "Next steps", "portal": "Official service page",
        "in_person": "Note: this service is applied for in person.",
        "disclaimer": "Note: TAMKEEN does not submit anything on your behalf, and acceptance is not guaranteed.",
    },
}


def _fallback_report_text(data):
    return build_report_text(data)


# ---- helpers and callbacks ----
def lang():
    return st.session_state.lang


def tr(key):
    return TEXTS[lang()].get(key, key)


def fld(data, key, default=""):
    return data.get(f"{key}_{lang()}") or data.get(key) or data.get(f"{key}_ar") or default


def as_list(value):
    if isinstance(value, list):
        return value
    return [value] if value else []


def disability_label(key, emoji=True):
    for disability_key, icon, arabic_name, english_name in DISABILITY_TYPES:
        if disability_key == key:
            name = arabic_name if lang() == "ar" else english_name
            return f"{icon} {name}" if emoji else name
    return key


def init_state():
    defaults = {
        "lang": "ar",
        "page": "home",
        "disability": None,
        "service": None,
        "docs": {},
        "nid": "",
        "nid_result": None,
        "nid_data": None,
        "include_id": False,
        "report_path": None,
        "show_panel": True,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def toggle_lang():
    st.session_state.lang = "en" if st.session_state.lang == "ar" else "ar"


def clear_report():
    st.session_state.report_path = None

def toggle_panel():
    st.session_state.show_panel = not st.session_state.show_panel


def go(page):
    st.session_state.page = page


def pick_disability(key):
    if st.session_state.disability != key:
        st.session_state.service = None
        st.session_state.report_path = None
    st.session_state.disability = key
    st.session_state.page = "services"


def pick_service(service):
    st.session_state.service = service
    st.session_state.report_path = None
    st.session_state.page = "checklist"


def toggle_doc(service_id, doc_id, widget_key):
    have = st.session_state.docs.setdefault(service_id, [])
    checked = st.session_state[widget_key]
    if checked and doc_id not in have:
        have.append(doc_id)
    elif not checked and doc_id in have:
        have.remove(doc_id)
    st.session_state.report_path = None


def save_progress():
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    session = st.session_state
    payload = {
        "disability": session.disability,
        "service": session.service,
        "docs": session.docs,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
    }
    PROGRESS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    st.session_state.flash = ("success", tr("saved"))


def load_progress():
    try:
        payload = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        st.session_state.flash = ("warning", tr("no_saved"))
        return
    session = st.session_state
    session.disability = payload.get("disability")
    session.service = payload.get("service")
    session.docs = payload.get("docs", {})
    session.report_path = None
    st.session_state.flash = ("success", tr("loaded"))


def docs_status():
    """Return the document readiness percentage and missing document IDs."""
    service = st.session_state.service
    if not service:
        return 0.0, []
    required_documents = service.get("documents", [])
    if not required_documents:
        return 0.0, []
    available_ids = st.session_state.docs.get(service["id"], [])
    result = get_checklist(required_documents, available_ids)
    return float(result.get("percent", 0)), list(result.get("missing", []))


# ----------------------------------------------------------------------------------
# Styling
# ----------------------------------------------------------------------------------
def inject_css():
    rtl = lang() == "ar"
    font = "'Cairo', sans-serif" if rtl else "'Poppins', 'Cairo', sans-serif"
    direction = "rtl" if rtl else "ltr"
    align = "right" if rtl else "left"
    side = "right" if rtl else "left"          # طرف اللوح (بيتعكس مع اللغة)
    inner = "left" if rtl else "right"         # الحد الداخلي للوح
    panel_w = 290
    # لما اللوح مفتوح: المحتوى بياخد العرض الباقي ومتزاح ناحية الطرف المقابل للوح
    main_shift = (
        f".block-container {{ width: calc(100% - {panel_w}px) !important; "
        f"margin-{side}: {panel_w}px !important; margin-{inner}: auto !important; }}"
        if st.session_state.show_panel else ""
    )
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Poppins:wght@400;600;700&display=swap');

        :root {{
            --tk-primary: #475569;
            --tk-primary-dark: #334155;
            --tk-secondary: #B4C0CE;
            --tk-soft: #E6EBF0;
            --tk-bg: #F4F6F8;
            --tk-ink: #1F2937;
            --tk-line: #DDE3EA;
            --tk-muted: #6B7785;
        }}
        html, body, [class*="st-"], .stApp {{ font-family: {font}; }}
        /* رجّع خط الأيقونات (السهم بتاع القايمة وغيره) عشان ما يظهرش اسمها كنص */
        [data-testid="stIconMaterial"],
        span[class*="material-symbols"],
        .material-icons, .material-symbols-rounded, .material-symbols-outlined {{
            font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons' !important;
            font-weight: normal !important;
            font-style: normal !important;
            letter-spacing: normal !important;
            text-transform: none !important;
            direction: ltr !important;
            -webkit-text-fill-color: currentColor !important;
        }}
        /* شيل شريط Deploy والقايمة من فوق، وسيب زرار فتح/قفل السايدبار */
        [data-testid="stToolbar"], [data-testid="stDeployButton"],
        .stDeployButton, [data-testid="stMainMenu"], [data-testid="stStatusWidget"] {{
            display: none !important;
        }}
        header[data-testid="stHeader"] {{
            background: transparent !important;
            box-shadow: none !important;
        }}
        .stApp {{
            background: var(--tk-bg);
        }}
        /* الاتجاه (RTL/LTR) على المحتوى بس، مش على هيكل الصفحة، عشان قفل القايمة الجانبية يشتغل صح */
        .block-container {{
            max-width: 1180px; padding-top: 2rem; direction: {direction};
            margin-left: auto; margin-right: auto;
        }}
        .stApp p, .stApp label, .stApp li, .stApp h1, .stApp h2, .stApp h3,
        .stApp .stCaption, .stApp .stMarkdown {{ text-align: {align}; }}

        .tk-brand {{ display: flex; align-items: center; gap: .7rem; }}
        .tk-brand-icon {{
            font-size: 2.2rem; background: white; border-radius: 18px;
            padding: .25rem .6rem; box-shadow: 0 6px 18px rgba(71,85,105,.16);
        }}
        .tk-brand-name {{
            font-size: 1.9rem; font-weight: 700; letter-spacing: .06em;
            color: var(--tk-primary);
        }}
        .tk-tagline {{ color: var(--tk-muted); font-size: .95rem; margin-top: -.2rem; }}

        .tk-hero {{
            background: var(--tk-primary);
            color: white; border-radius: 24px; padding: 1.6rem 1.8rem;
            box-shadow: 0 10px 26px rgba(71,85,105,.2); margin-bottom: 1.2rem;
        }}
        .tk-hero h2 {{ margin: 0 0 .4rem 0; color: white; }}
        .tk-hero p {{ margin: 0; opacity: .95; line-height: 1.8; }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: #FFFFFF; border-radius: 20px !important;
            border: 1px solid var(--tk-line) !important;
            box-shadow: 0 6px 20px rgba(31,41,55,.06);
        }}
        .stButton > button, .stDownloadButton > button, .stLinkButton > a {{
            border-radius: 14px; font-weight: 600; border: 1px solid var(--tk-secondary);
            color: var(--tk-ink);
            transition: transform .15s ease, box-shadow .15s ease;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            transform: translateY(-2px); box-shadow: 0 8px 18px rgba(71,85,105,.18);
            border-color: var(--tk-primary); color: var(--tk-primary);
        }}
        .stButton > button[kind="primary"], .stButton > button[data-testid="stBaseButton-primary"],
        .stLinkButton > a[kind="primary"], .stLinkButton > a[data-testid="stBaseLinkButton-primary"] {{
            background: var(--tk-primary); color: white !important; border: none;
        }}
        .stButton > button[kind="primary"]:hover, .stButton > button[data-testid="stBaseButton-primary"]:hover,
        .stLinkButton > a[kind="primary"]:hover, .stLinkButton > a[data-testid="stBaseLinkButton-primary"]:hover {{
            background: var(--tk-primary-dark); color: white !important;
        }}
        .stProgress > div > div > div > div {{
            background: var(--tk-primary);
        }}
        .stProgress > div > div {{
            background: var(--tk-soft); border-radius: 10px; padding: 2px 10px;
        }}
        /* نقط القوايم تفضل جوه الكارت (في العربي كانت بتطلع بره الحافة) */
        .stApp ul, .stApp ol {{
            list-style-position: inside !important;
            padding: 0 .5rem !important; margin: .3rem 0 !important;
        }}
        .stApp li {{ margin: .15rem 0 !important; }}
        .stTextArea textarea {{ direction: {direction}; text-align: {align}; line-height: 1.8; }}
        [data-testid="stExpander"] details {{ border-radius: 14px; overflow: hidden; }}
        [data-testid="stExpander"] details > div {{ padding-left: 1rem; padding-right: 1rem; }}
        .tk-chip {{
            display: inline-block; padding: .15rem .7rem; border-radius: 999px;
            background: var(--tk-soft); color: var(--tk-primary); font-size: .85rem;
            font-weight: 600; margin: .1rem;
        }}
        /* اللوح الجانبي الثابت */
        .st-key-side_panel {{
            position: fixed; top: 0; bottom: 0; {side}: 0; width: {panel_w}px;
            z-index: 1000001; overflow-y: auto; direction: {direction};
            background: rgba(255,255,255,.98);
            border-{inner}: 1px solid var(--tk-line);
            box-shadow: 0 0 30px rgba(31,41,55,.08);
            padding: 1rem;
        }}
        .st-key-panel_open {{
            position: fixed; top: .9rem; {side}: .9rem;
            z-index: 1000001; width: auto !important;
        }}
        {main_shift}
        @media (max-width: 768px) {{
            .st-key-side_panel {{ width: 85vw; }}
            .block-container {{
                width: 100% !important;
                margin-left: 0 !important; margin-right: 0 !important;
            }}
        }}
        #MainMenu, footer {{ visibility: hidden; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------------------------------------------------------------
# Layout pieces
# ----------------------------------------------------------------------------------
def header():
    c1, c2 = st.columns([5, 1.3])
    with c1:
        st.markdown(
            f"""
            <div class="tk-brand">
                <span class="tk-brand-icon">🎓</span>
                <div>
                    <div class="tk-brand-name">TAMKEEN</div>
                    <div class="tk-tagline">{tr('tagline')}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.button(tr("lang_btn"), on_click=toggle_lang, use_container_width=True, key="lang_toggle")


def page_enabled(page):
    s = st.session_state
    if page in ("home",):
        return True
    if page == "services":
        return s.disability is not None
    return s.service is not None


def nav():
    st.write("")
    cols = st.columns(len(PAGES))
    for col, page in zip(cols, PAGES):
        with col:
            st.button(
                tr(f"nav_{page}"),
                key=f"nav_{page}",
                on_click=go,
                args=(page,),
                disabled=not page_enabled(page),
                type="primary" if st.session_state.page == page else "secondary",
                use_container_width=True,
            )
    st.write("")


def step_status():
    """حالة كل خطوة: done / missing / review (Feature 6)."""
    s = st.session_state
    percent, _ = docs_status()
    if not s.service:
        docs = "missing"
    elif percent >= 100:
        docs = "done"
    elif percent > 0:
        docs = "review"
    else:
        docs = "missing"
    return {
        "p_service": "done" if s.service else "missing",
        "p_docs": docs,
        "p_id": "done" if (s.nid_result and s.nid_result["valid"]) else "missing",
        "p_report": "done" if s.report_path else "missing",
    }


def keyed_container(key):
    """container بمفتاح عشان نثبّته بالـ CSS (st.container(key=...) في Streamlit الحديث)."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def panel_open_button():
    """زرار فتح القايمة: بيظهر على نفس طرف اللوحة لما تكون مقفولة."""
    with keyed_container("panel_open"):
        st.button(tr("menu"), on_click=toggle_panel, key="panel_open_btn")


def side_panel():
    s = st.session_state
    icons = {"done": "✅", "missing": "⬜", "review": "🟡"}
    names = {"done": tr("st_done"), "missing": tr("st_missing"), "review": tr("st_review")}
    with keyed_container("side_panel"):
        st.button(tr("menu_close"), on_click=toggle_panel, use_container_width=True, key="panel_close_btn")
        st.markdown(f"### 🎓 {tr('progress')}")
        percent, _ = docs_status()
        st.progress(min(percent / 100, 1.0), text=f"{percent:.0f}%")
        for key, status in step_status().items():
            st.markdown(f"{icons[status]} **{tr(key)}** — {names[status]}")
        st.divider()
        st.button(tr("save"), on_click=save_progress, use_container_width=True, key="save_btn")
        st.button(tr("load"), on_click=load_progress, use_container_width=True, key="load_btn")
        flash = s.pop("flash", None)
        if flash:
            getattr(st, flash[0])(flash[1])
        if demo_mode():
            st.divider()
            st.caption(tr("demo_note"))


def nav_buttons(back=None, nxt=None, nxt_disabled=False):
    st.write("")
    c1, c2, _ = st.columns([1, 1, 2])
    if back:
        c1.button(tr("back"), on_click=go, args=(back,), key=f"back_{back}", use_container_width=True)
    if nxt:
        c2.button(tr("next"), on_click=go, args=(nxt,), key=f"next_{nxt}",
                  disabled=nxt_disabled, type="primary", use_container_width=True)


# ----------------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------------
def page_home():
    st.markdown(
        f"""<div class="tk-hero"><h2>{tr('hero_title')}</h2><p>{tr('hero_text')}</p></div>""",
        unsafe_allow_html=True,
    )
    st.subheader(tr("choose_type"))
    cols = st.columns(2)
    for i, (key, emoji, ar, en) in enumerate(DISABILITY_TYPES):
        with cols[i % 2]:
            with st.container(border=True):
                st.markdown(f"<div style='font-size:2.4rem;text-align:center'>{emoji}</div>",
                            unsafe_allow_html=True)
                st.button(
                    ar if lang() == "ar" else en,
                    key=f"dis_{key}",
                    on_click=pick_disability,
                    args=(key,),
                    type="primary" if st.session_state.disability == key else "secondary",
                    use_container_width=True,
                )


def page_services():
    s = st.session_state
    st.subheader(f"{tr('services_title')} — {disability_label(s.disability, emoji=False)}")
    try:
        services = get_services(s.disability)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        st.error(tr("load_error"))
        return
    if not services:
        st.info(tr("no_services"))
        nav_buttons(back="home")
        return

    for svc in services:
        with st.container(border=True):
            st.markdown(f"### {fld(svc, 'name')}")
            if fld(svc, "authority"):
                st.markdown(f"<span class='tk-chip'>🏛️ {tr('authority')}: {fld(svc, 'authority')}</span>",
                            unsafe_allow_html=True)
            st.write(fld(svc, "description"))
            with st.expander(tr("eligibility")):
                for item in as_list(fld(svc, "eligibility")):
                    st.markdown(f"- {item}")
            st.caption(
                f"{tr('source')}: {svc.get('source', '—')}  •  "
                f"{tr('last_reviewed')}: {svc.get('last_reviewed', '—')}"
            )
            st.button(tr("choose"), key=f"choose_{svc['id']}", on_click=pick_service,
                      args=(svc,), type="primary")
    nav_buttons(back="home")


def page_checklist():
    s = st.session_state
    svc = s.service
    st.subheader(f"{tr('checklist_title')} — {fld(svc, 'name')}")
    st.caption(tr("checklist_hint"))

    docs = svc.get("documents", [])
    if svc.get("docs_generic"):
        st.info(tr("generic_docs_notice"))
    if not docs:
        st.info(tr("no_docs"))
        nav_buttons(back="services", nxt="national_id")
        return
    have = s.docs.setdefault(svc["id"], [])
    with st.container(border=True):
        for d in docs:
            key = f"cb_{svc['id']}_{d['id']}"
            st.checkbox(
                fld(d, "name"),
                value=d["id"] in have,
                key=key,
                on_change=toggle_doc,
                args=(svc["id"], d["id"], key),
            )

    percent, missing_ids = docs_status()
    c1, c2 = st.columns(2)
    c1.metric(tr("ready"), f"{percent:.0f}%")
    c2.metric(tr("missing_docs"), len(missing_ids))
    st.progress(min(percent / 100, 1.0))

    if missing_ids:
        names = [fld(d, "name") for d in docs if d["id"] in missing_ids]
        st.warning(tr("missing_warn") + "\n\n" + "\n".join(f"- {n}" for n in names))
    else:
        st.success(tr("all_ready"))
    nav_buttons(back="services", nxt="national_id")


def page_national_id():
    s = st.session_state
    st.subheader(tr("id_title"))
    st.caption(tr("id_hint"))
    st.warning(tr("id_disclaimer"))

    with st.container(border=True):
        nid = st.text_input(tr("id_input"), value=s.nid, max_chars=14, key="nid_input")
        if st.button(tr("id_check"), type="primary", key="nid_check"):
            s.nid = nid.strip()
            s.nid_result = validate_id(s.nid)
            s.nid_data = extract_id(s.nid) if s.nid_result["valid"] else None
            s.report_path = None

        res = s.nid_result
        if res and s.nid == nid.strip():
            if res["valid"]:
                st.success(tr("id_valid"))
                data = s.nid_data or {}
                gov = data.get("governorate")
                if isinstance(gov, dict):
                    gov = gov.get(lang()) or gov.get("ar") or gov.get("en")
                gender = data.get("gender")
                cols = st.columns(3 if gender in ("male", "female") else 2)
                cols[0].metric(tr("birth_date"), data.get("birth_date") or "—")
                cols[1].metric(tr("governorate"), gov or tr("unknown_gov"))
                if gender in ("male", "female"):
                    cols[2].metric(tr("gender"), tr(gender))
                s.include_id = st.checkbox(tr("id_consent"), value=s.include_id, key="id_consent_cb",
                                           on_change=clear_report)
            else:
                err = res.get("error")
                st.error(TEXTS[lang()].get(f"err_{err}", err or ""))
    nav_buttons(back="checklist", nxt="summary")


def build_report_data():
    s = st.session_state
    svc = s.service
    docs = svc.get("documents", [])
    have_ids = s.docs.get(svc["id"], [])
    user_data = {}
    if s.include_id and s.nid_result and s.nid_result["valid"] and s.nid_data:
        user_data = {
            key: s.nid_data.get(key)
            for key in ("birth_date", "governorate")
            if s.nid_data.get(key)
        }
    return {
        "service": fld(svc, "name"),
        "authority": fld(svc, "authority"),
        "user_data": user_data,
        "docs_generic": bool(svc.get("docs_generic")),
        "docs_have": [fld(d, "name") for d in docs if d["id"] in have_ids],
        "docs_missing": [fld(d, "name") for d in docs if d["id"] not in have_ids],
        "next_steps": [tr("step1"), tr("step2"), tr("step3")],
        "official_url": svc.get("official_url", ""),
        "in_person": bool(svc.get("in_person")),
        "lang": lang(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }



def page_summary():
    render_summary_page(
        build_report_data=build_report_data,
        docs_status=docs_status,
        tr=tr,
        nav_buttons=nav_buttons
    )


ROUTES = {
    "home": page_home,
    "services": page_services,
    "checklist": page_checklist,
    "national_id": page_national_id,
    "summary": page_summary,
}


# ----------------------------------------------------------------------------------
# Entry point  (app.py: `import ui; ui.main()`)
# ----------------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="TAMKEEN", page_icon=app_icon(), layout="wide")
    init_state()
    inject_css()
    # اللوح ثابت على طرف الصفحة (يمين في العربي، شمال في الإنجليزي) وزرار القايمة جواه
    if st.session_state.show_panel:
        side_panel()
    else:
        panel_open_button()
    header()
    nav()
    page = st.session_state.page
    if not page_enabled(page):
        page = "home"
        st.session_state.page = page
    ROUTES[page]()


if __name__ == "__main__":
    main()
