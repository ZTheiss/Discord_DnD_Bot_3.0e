import fitz
import json
import os



pdf_path = "PHBK.pdf"
output_folder = "pdfreads"
json_output = "playershandbook.json"
os.makedirs(output_folder, exist_ok=True)

doc = fitz.open(pdf_path)
result = {"pages": []}

for page_number in range(doc.page_count):
    page = doc.load_page(page_number)

    # Extract text
    text = page.get_text()

    # Extract images
    images = page.get_images(full=True)
    image_files = []

    for img_index, img in enumerate(images, start=1):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)

        # Save image
        if pix.n < 5:  # RGB or grayscale
            img_path = f"{output_folder}/page{page_number+1}_img{img_index}.png"
            pix.save(img_path)
        else:  # CMYK
            pix_converted = fitz.Pixmap(fitz.csRGB, pix)
            img_path = f"{output_folder}/page{page_number+1}_img{img_index}.png"
            pix_converted.save(img_path)

        image_files.append(img_path)

    # Add page data to JSON structure
    result["pages"].append({
        "page_number": page_number + 1,
        "text": text,
        "images": image_files
    })

# Write JSON file
with open(json_output, "w", encoding="utf-8") as f:
    json.dump(result, f, indent=4, ensure_ascii=False)

print(f"JSON saved to {json_output}")

