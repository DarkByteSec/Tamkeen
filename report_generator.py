from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st

def _get_labels(language):
    """Return report labels based on the selected language."""

    if language == "en":
        return {
            "title": "TAMKEEN - Application Summary",
            "date": "Generated",
            "service": "Service",
            "authority": "Responsible Authority",
            "user": "User Information",
            "no_user": "No user information included.",
            "birth_date": "Birth Date",
            "governorate": "Governorate",
            "have": "Available Documents",
            "missing": "Missing Documents",
            "generic_docs_notice": "These documents are a general checklist, not official confirmation of this service's requirements.",
            "none": "None",
            "steps": "Next Steps",
            "portal": "Official Service Page",
            "in_person": "Note: This service requires in-person application.",
            "disclaimer": (
                "TAMKEEN does not submit applications on your behalf "
                "or guarantee acceptance."
            ),
        }

    return {
        "title": "TAMKEEN - ملخص الطلب",
        "date": "تاريخ الإنشاء",
        "service": "الخدمة",
        "authority": "الجهة المسؤولة",
        "user": "بيانات المستخدم",
        "no_user": "لم يتم إدراج بيانات المستخدم.",
        "birth_date": "تاريخ الميلاد",
        "governorate": "المحافظة",
        "have": "المستندات المتوفرة",
        "missing": "المستندات الناقصة",
        "generic_docs_notice": "هذه قائمة عامة للمساعدة وليست تأكيدًا رسميًا لمتطلبات الخدمة.",
        "none": "لا يوجد",
        "steps": "الخطوات التالية",
        "portal": "صفحة الخدمة الرسمية",
        "in_person": "ملحوظة: التقديم على هذه الخدمة يتم حضورياً.",
        "disclaimer": (
            "تنبيه: تمكين لا يقدم الطلب نيابة عنك، "
            "ولا يضمن قبول الطلب."
        ),
    }


def _get_governorate(user_data, language):
    """Handle governorate stored as text or as a bilingual dictionary."""

    governorate = user_data.get("governorate", "")

    if isinstance(governorate, dict):
        return (
            governorate.get(language)
            or governorate.get("ar")
            or governorate.get("en")
            or ""
        )

    return governorate


def build_report_text(data: dict) -> str:
    """Build the report content using the data received from ui.py."""

    language = data.get("lang", "ar")
    labels = _get_labels(language)
    separator = "=" * 45

    report = [
        labels["title"],
        separator,
        f"{labels['date']}: {data.get('generated_at', '')}",
        "",
        f"{labels['service']}: {data.get('service', '')}",
    ]

    authority = data.get("authority")
    if authority:
        report.append(f"{labels['authority']}: {authority}")

    # User information
    report.extend(["", f"{labels['user']}:"])

    user_data = data.get("user_data") or {}

    if user_data:
        birth_date = user_data.get("birth_date", "")
        governorate = _get_governorate(user_data, language)

        if birth_date:
            report.append(f"  - {labels['birth_date']}: {birth_date}")

        if governorate:
            report.append(f"  - {labels['governorate']}: {governorate}")

    else:
        report.append(f"  {labels['no_user']}")

    # IMPORTANT: Never include the full National ID in this report.

    if data.get("docs_generic"):
        report.extend(["", labels["generic_docs_notice"]])

    # Available documents
    report.extend(["", f"{labels['have']}:"])
    available = data.get("docs_have", [])

    if available:
        report.extend([f"  [x] {doc}" for doc in available])
    else:
        report.append(f"  {labels['none']}")

    # Missing documents
    report.extend(["", f"{labels['missing']}:"])
    missing = data.get("docs_missing", [])

    if missing:
        report.extend([f"  [ ] {doc}" for doc in missing])
    else:
        report.append(f"  {labels['none']}")

    # Next steps
    report.extend(["", f"{labels['steps']}:"])

    for number, step in enumerate(data.get("next_steps", []), start=1):
        report.append(f"  {number}. {step}")

    # Official service page
    official_url = data.get("official_url")
    if official_url:
        report.extend(["", f"{labels['portal']}: {official_url}"])

    if data.get("in_person"):
        report.extend(["", labels["in_person"]])

    report.extend([
        "",
        separator,
        labels["disclaimer"],
    ])

    return "\n".join(report) + "\n"


def generate_report(data: dict) -> str:
    """Create the TXT report and return its file path."""

    reports_folder = Path("data") / "reports"
    reports_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    report_text = build_report_text(data)
    while True:
        file_path = reports_folder / f"tamkeen_summary_{timestamp}_{uuid4().hex}.txt"
        try:
            with file_path.open("x", encoding="utf-8") as report_file:
                report_file.write(report_text)
            return str(file_path)
        except FileExistsError:
            continue


# Compatibility with the existing import in ui.py
def make_report(data):
    return generate_report(data)


def render_summary_page(build_report_data, docs_status, tr, nav_buttons):
    """Render the summary page in the Streamlit app."""

    s = st.session_state
    svc = s.service

    st.subheader(tr("summary_title"))

    # Collect summary data
    data = build_report_data()

    with st.container(border=True):

        st.markdown(f"**{tr('selected')}:** {data['service']}")

        if data["authority"]:
            st.markdown(f"**{tr('authority')}:** {data['authority']}")

        if data.get("docs_generic"):
            st.info(tr("generic_docs_notice"))

        # Documents progress
        percent, _ = docs_status()

        st.progress(
            min(percent / 100, 1.0),
            text=f"{tr('ready')}: {percent:.0f}%"
        )

        if not svc.get("documents"):
            st.info(tr("no_docs"))

        elif data["docs_missing"]:
            st.warning(
                tr("missing_warn")
                + "\n\n"
                + "\n".join(
                    f"- {name}" for name in data["docs_missing"]
                )
            )

        else:
            st.success(tr("all_ready"))

        # Generate report
        if st.button(
            tr("gen_report"),
            type="primary",
            key="gen_report"
        ):
            try:
                s.report_path = generate_report(data)
                st.success(tr("report_ready"))

            except OSError:
                st.error(tr("report_error"))

        # Display and download report
        report_path = s.get("report_path")

        if report_path and Path(report_path).exists():

            report_text = Path(report_path).read_text(
                encoding="utf-8"
            )

            st.text_area(
                " ",
                report_text,
                height=240,
                label_visibility="collapsed"
            )

            st.download_button(
                tr("download"),
                report_text,
                file_name=Path(report_path).name,
                mime="text/plain",
                key="dl_report"
            )

    # Official portal section
    st.markdown(f"### {tr('portal_title')}")

    with st.container(border=True):

        if svc.get("in_person"):
            st.warning(tr("in_person"))

        st.info(tr("last_step"))

        url = svc.get("official_url")

        if url:
            st.link_button(
                tr("open_portal"),
                url,
                type="primary"
            )
        else:
            st.caption(tr("no_url"))

        st.caption(tr("portal_disclaimer"))

    # Navigation
    nav_buttons(back="national_id")

