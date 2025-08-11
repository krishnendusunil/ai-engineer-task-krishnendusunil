# checklist.py
REQUIRED = {
  "Company Incorporation": [
      "Articles of Association",
      "Memorandum of Association",
      "Incorporation Application Form",
      "UBO Declaration Form",
      "Register of Members and Directors"
  ]
}

def detect_process(doc_types):
    # naive: if majority of uploaded types match incorporation items
    inc_count = sum(1 for t in doc_types if t in REQUIRED["Company Incorporation"])
    if inc_count >= 2:
        return "Company Incorporation"
    return "Unknown"

def compare(uploaded_types, process_name):
    required = REQUIRED.get(process_name, [])
    missing = [r for r in required if r not in uploaded_types]
    return {"process": process_name, "uploaded": len(uploaded_types), "required": len(required), "missing": missing}
