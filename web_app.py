
import streamlit as st
import hashlib
import csv
import io
from collections import defaultdict

st.set_page_config(
    page_title="Duplicate File Finder",
    page_icon="📂",
    layout="wide"
)

st.title("📂 Duplicate File Finder and Organizer")
st.write(
    "Upload files to find duplicates, filter results, "
    "and download a CSV report."
)

st.info(
    "Your files are processed in this app session. "
    "Only upload files you are comfortable sharing with this service."
)

uploaded_files = st.file_uploader(
    "Choose files to scan",
    accept_multiple_files=True
)

col1, col2 = st.columns(2)

with col1:
    extensions_text = st.text_input(
        "File extensions (comma-separated)",
        placeholder="Example: .pdf, .jpg, .txt — leave blank for all"
    )

with col2:
    min_size_kb = st.number_input(
        "Minimum file size (KB)",
        min_value=0,
        value=0,
        step=1
    )

if st.button("🔍 Find Duplicates", type="primary"):
    if not uploaded_files:
        st.warning("Please upload at least one file.")
    else:
        allowed_extensions = {
            ext.strip().lower()
            if ext.strip().startswith(".")
            else "." + ext.strip().lower()
            for ext in extensions_text.split(",")
            if ext.strip()
        }

        min_size_bytes = min_size_kb * 1024
        hash_groups = defaultdict(list)

        for file in uploaded_files:
            content = file.getvalue()
            extension = "." + file.name.rsplit(".", 1)[-1].lower() \
                if "." in file.name else ""

            if allowed_extensions and extension not in allowed_extensions:
                continue

            if len(content) < min_size_bytes:
                continue

            file_hash = hashlib.sha256(content).hexdigest()

            hash_groups[file_hash].append({
                "filename": file.name,
                "size_bytes": len(content),
                "sha256": file_hash
            })

        duplicate_groups = [
            files for files in hash_groups.values()
            if len(files) > 1
        ]

        st.session_state["duplicate_groups"] = duplicate_groups
        st.session_state["scan_complete"] = True

if st.session_state.get("scan_complete", False):
    groups = st.session_state.get("duplicate_groups", [])

    st.subheader("📊 Scan Results")
    st.metric("Duplicate groups found", len(groups))
    st.metric(
        "Files in duplicate groups",
        sum(len(group) for group in groups)
    )

    if not groups:
        st.success("No duplicate files found with the selected filters.")
    else:
        csv_rows = []

        for group_number, group in enumerate(groups, start=1):
            st.markdown(f"### Duplicate Group {group_number}")

            for file in group:
                st.write(f"📄 **{file['filename']}**")
                st.caption(
                    f"Size: {file['size_bytes']:,} bytes"
                )

                csv_rows.append({
                    "group_number": group_number,
                    "filename": file["filename"],
                    "size_bytes": file["size_bytes"],
                    "sha256": file["sha256"]
                })

            st.divider()

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                "group_number",
                "filename",
                "size_bytes",
                "sha256"
            ]
        )
        writer.writeheader()
        writer.writerows(csv_rows)

        st.download_button(
            label="⬇️ Download CSV Report",
            data=output.getvalue(),
            file_name="duplicate_findings.csv",
            mime="text/csv"
        )
