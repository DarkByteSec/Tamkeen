"""
checklist.py — Document Checklist (الشخص التاني)

منطق فقط، من غير واجهة. الواجهة بتتعمل في ui.py (Streamlit).
المستندات ممكن تيجي بأي شكل من دول:
    "تقرير طبي"
    {"id": "d1", "name": "تقرير طبي"}
    {"id": "d1", "name": {"ar": "تقرير طبي", "en": "Medical report"}}
    {"id": "d1", "name_ar": "تقرير طبي", "name_en": "Medical report"}
"""

MESSAGES = {
    "ar": {
        "available": "متوفر",
        "missing": "ناقص",
        "warning_missing": "لسه ناقصك {n} مستند. راجع القائمة قبل ما تكمل.",
        "warning_complete": "كل المستندات المطلوبة جاهزة.",
        "warning_empty": "مفيش مستندات مطلوبة متسجلة للخدمة دي.",
    },
    "en": {
        "available": "Available",
        "missing": "Missing",
        "warning_missing": "You're still missing {n} document(s). Review the list before you continue.",
        "warning_complete": "All required documents are ready.",
        "warning_empty": "No required documents are listed for this service.",
    },
}


# ---------------------------------------------------------------------------
# مساعدات: استخراج الاسم والـ id من المستند بأي شكل
# ---------------------------------------------------------------------------
def _text(value, lang):
    if isinstance(value, dict):
        return value.get(lang) or value.get("ar") or value.get("en") or ""
    return str(value)


def _doc_name(document, lang="ar"):
    if isinstance(document, dict):
        if "name" in document:
            return _text(document["name"], lang)
        return (
            document.get(f"name_{lang}")
            or document.get("name_ar")
            or document.get("name_en")
            or ""
        )
    return str(document)


def _doc_id(document, lang="ar"):
    if isinstance(document, dict) and document.get("id") is not None:
        return document["id"]
    return _doc_name(document, lang)


# ---------------------------------------------------------------------------
# 1. Checklist Logic
# ---------------------------------------------------------------------------
def evaluate_checklist(required_documents, user_choices, lang="ar"):
    """
    تستقبل:
        required_documents: قائمة المستندات المطلوبة (بأي شكل من اللي فوق).
        user_choices: قاموس {اسم المستند أو الـ id: True/False}.
        lang: "ar" أو "en" للتنبيهات وأسماء الحالات.

    ترجع Dictionary فيه المستندات المكتملة والناقصة والنسبة ورسالة التنبيه.
    """
    msg = MESSAGES.get(lang, MESSAGES["ar"])

    documents = []
    completed = []
    missing = []

    for document in required_documents:
        name = _doc_name(document, lang)
        doc_id = _doc_id(document, lang)

        # الاختيار ممكن يتسجل بالـ id أو بالاسم
        is_available = bool(user_choices.get(doc_id, user_choices.get(name, False)))

        documents.append({
            "id": doc_id,
            "name": name,
            "available": is_available,
            "status": msg["available"] if is_available else msg["missing"],
        })

        (completed if is_available else missing).append(name)

    total = len(documents)
    completed_count = len(completed)
    percentage = (completed_count / total) * 100 if total > 0 else 0

    if total == 0:
        warning = msg["warning_empty"]
    elif missing:
        warning = msg["warning_missing"].format(n=len(missing))
    else:
        warning = msg["warning_complete"]

    return {
        "required_documents": [item["name"] for item in documents],
        "documents": documents,
        "completed_documents": completed,
        "missing_documents": missing,
        "total_documents": total,
        "completed_count": completed_count,
        "missing_count": len(missing),
        "completion_percentage": round(percentage, 2),
        "warning": warning,
        # قايمة فاضية = مفيش حاجة تتأكد منها، فمش "مكتملة"
        "is_complete": total > 0 and len(missing) == 0,
    }


def check_documents(required_docs, available_ids, lang="ar"):
    """
    الدالة اللي بتناديها الواجهة.
        required_docs: قائمة المستندات (فيها id)
        available_ids: قايمة الـ ids اللي المستخدم علّم عليها
    ترجع: {"percent", "missing": [ids], "completed": [ids], "warning", "is_complete"}
    """
    chosen = set(available_ids)
    ids = [_doc_id(d, lang) for d in required_docs]
    choices = {doc_id: (doc_id in chosen) for doc_id in ids}

    result = evaluate_checklist(required_docs, choices, lang)

    return {
        "percent": result["completion_percentage"],
        "missing": [i for i in ids if not choices[i]],
        "completed": [i for i in ids if choices[i]],
        "warning": result["warning"],
        "is_complete": result["is_complete"],
    }


# ---------------------------------------------------------------------------
# 2. Final Report Data
# ---------------------------------------------------------------------------
def generate_checklist_summary(required_documents, user_choices, lang="ar"):
    """Return checklist evaluation and text; the application report is built separately."""
    result = evaluate_checklist(required_documents, user_choices, lang)

    lines = [
        "Tamkeen - Checklist Summary",
        "=" * 35,
        f"Total documents: {result['total_documents']}",
        f"Completed: {result['completed_count']}",
        f"Missing: {result['missing_count']}",
        f"Completion: {result['completion_percentage']}%",
        "",
        "Document Details:",
    ]
    for document in result["documents"]:
        lines.append(f"- {document['name']}: {document['status']}")

    lines.extend(["", f"Message: {result['warning']}"])

    result["report_text"] = "\n".join(lines)
    return result


# ---------------------------------------------------------------------------
# مثال تشغيل سريع من الـ terminal (مش بيشتغل وقت الـ import)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    service_documents = [
        {"id": "d1", "name": {"ar": "صورة بطاقة الرقم القومي", "en": "National ID copy"}},
        {"id": "d2", "name": {"ar": "تقرير طبي", "en": "Medical report"}},
        {"id": "d3", "name": {"ar": "صورة شخصية", "en": "Personal photo"}},
    ]
    print(check_documents(service_documents, ["d1", "d3"]))
