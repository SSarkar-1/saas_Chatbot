import json
from typing import List

# Unstructured document parsing
from unstructured.partition.pdf import partition_pdf




def partition_document(file_path:str):
    """Extract element from PDF using unstructured"""
    print(f"Partioning document : {file_path}")

    elements=partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,
        extract_image_block_types=["Image"],
        extract_image_block_to_payload=True
    )

    print(f"✅ Extracted {len(elements)} elements")
    return elements
# Test
# file_path="data/attention-is-all-you-need.pdf"
# elements=partition_document(file_path)

