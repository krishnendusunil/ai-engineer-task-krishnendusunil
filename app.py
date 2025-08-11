import streamlit as st
from io import BytesIO
from pathlib import Path
import json
import os
import shutil


from reviewer import analyze_single_file, analyze_uploads_folder, UPLOADS_DIR, REVIEWED_DIR, REPORTS_DIR

st.set_page_config(page_title="ADGM Corporate Agent — Reviewer", layout="wide")

st.title("ADGM Corporate Agent — Document Reviewer (Multi-file)")

st.markdown(
    """
Upload one or more `.docx` files. The system will:
- Run RAG-based compliance checks (using your FAISS + Gemini setup),
- Insert inline review notes into `.docx` (saved under `reviewed/`),
- Generate a combined JSON checklist + per-file issue report (saved under `reports/combined_review_report.json`).
"""
)

# ensure directories exist
Path(UPLOADS_DIR).mkdir(exist_ok=True)
Path(REVIEWED_DIR).mkdir(exist_ok=True)
Path(REPORTS_DIR).mkdir(exist_ok=True)

uploaded_files = st.file_uploader("Upload .docx files (multi-select allowed)", type=["docx"], accept_multiple_files=True)

if st.button("Run Review"):

    if not uploaded_files:
        st.warning("Please upload one or more .docx files first.")
        st.stop()

    # Clear uploads folder (optional) or you can keep existing files
    # here we clear and re-save to keep things predictable
    for p in Path(UPLOADS_DIR).glob("*"):
        try:
            p.unlink()
        except Exception:
            pass

    saved_paths = []
    for f in uploaded_files:
        out_path = Path(UPLOADS_DIR) / f.name
        with open(out_path, "wb") as fp:
            fp.write(f.getbuffer())
        saved_paths.append(str(out_path))

    st.info(f"Saved {len(saved_paths)} files to `{UPLOADS_DIR}/` — starting analysis...")

    # Use your batch analyzer (will also write combined JSON)
    try:
        combined_report = analyze_uploads_folder(UPLOADS_DIR)
    except Exception as e:
        st.error(f"Error while running analysis: {e}")
        raise

    # Show checklist summary
    st.subheader("Checklist Summary")
    st.markdown(f"**Detected process:** `{combined_report['process']}`")
    st.markdown(f"**Uploaded documents:** {combined_report['documents_uploaded']}")
    st.markdown(f"**Required documents (for process):** {combined_report['required_documents']}")
    if combined_report["missing_documents"]:
        st.markdown(f"**Missing documents:** <span style='color:red'>{combined_report['missing_documents']}</span>", unsafe_allow_html=True)
    else:
        st.markdown(f"**Missing documents:** <span style='color:green'>None</span>", unsafe_allow_html=True)

    # Display per-file issues
    st.subheader("Per-file Findings")
    for file_res in combined_report["per_file_results"]:
        st.markdown(f"### {Path(file_res['file']).name} — Type: **{file_res.get('doc_type','Unknown')}**")

        issues = file_res.get("issues", [])
        if not issues:
            st.success("No issues found.")
            continue

        # Build a simple HTML table with colored severity badges
        rows_html = []
        rows_html.append(
            "<table style='width:100%; border-collapse: collapse;'>"
            "<thead><tr style='text-align:left; border-bottom:1px solid #ddd;'>"
            "<th style='padding:6px;'>Section</th><th style='padding:6px;'>Issue</th><th style='padding:6px;'>Severity</th><th style='padding:6px;'>Suggestion</th><th style='padding:6px;'>Reference</th>"
            "</tr></thead><tbody>"
        )
        for it in issues:
            sev = (it.get("severity") or "").lower()
            if sev == "high":
                sev_html = "<span style='background:#ff4d4d;color:white;padding:4px 8px;border-radius:4px;'>HIGH</span>"
            elif sev == "medium":
                sev_html = "<span style='background:#ffcc00;color:black;padding:4px 8px;border-radius:4px;'>MED</span>"
            elif sev == "low":
                sev_html = "<span style='background:#90ee90;color:black;padding:4px 8px;border-radius:4px;'>LOW</span>"
            else:
                sev_html = f"<span style='padding:4px 8px;border-radius:4px;background:#ddd'>{it.get('severity','')}</span>"

            rows_html.append(
                "<tr style='border-bottom:1px solid #eee;'>"
                f"<td style='padding:6px;vertical-align:top'>{it.get('document_section','')}</td>"
                f"<td style='padding:6px;vertical-align:top'>{it.get('issue','')}</td>"
                f"<td style='padding:6px;vertical-align:top'>{sev_html}</td>"
                f"<td style='padding:6px;vertical-align:top'>{it.get('suggestion','')}</td>"
                f"<td style='padding:6px;vertical-align:top'>{it.get('source_reference','')}</td>"
                "</tr>"
            )
        rows_html.append("</tbody></table>")
        table_html = "\n".join(rows_html)
        st.markdown(table_html, unsafe_allow_html=True)

        # Download reviewed doc if present
        if file_res.get("reviewed_file"):
            reviewed_path = Path(file_res["reviewed_file"])
            if reviewed_path.exists():
                with open(reviewed_path, "rb") as f:
                    btn = st.download_button(
                        label=f"Download reviewed: {reviewed_path.name}",
                        data=f.read(),
                        file_name=reviewed_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )

    # Combined JSON download
    combined_json_path = Path(REPORTS_DIR) / "combined_review_report.json"
    if combined_json_path.exists():
        with open(combined_json_path, "rb") as fh:
            st.download_button("Download combined JSON report", fh.read(), file_name=combined_json_path.name, mime="application/json")

    st.success("Analysis complete.")
