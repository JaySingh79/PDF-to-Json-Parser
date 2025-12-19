import cv2
import numpy as np
import pytesseract
import torch
from pdf2image import convert_from_path
from PIL import Image
import json
from ultralytics import YOLO

# -------------------------------
# STEP 1: PDF to Images
# -------------------------------
def pdf_to_images(pdf_path, dpi=300):
    return convert_from_path(pdf_path, poppler_path="poppler-25.07.0/Library/bin", dpi=dpi)

# -------------------------------
# STEP 2: Load YOLOv5 Model (for chart detection & classification)
# -------------------------------
def load_yolo(model_path="yolov5_charts.pt"):
    # model = torch.hub.load("ultralytics/yolov5", "custom", path=model_path, force_reload=False)
    model= YOLO(model_path)
    return model

# -------------------------------
# STEP 3: Chart-specific extraction
# -------------------------------

def extract_bar_chart(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bars = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > 20 and w < 100:  # simple filter for bars
            bars.append({"label": f"bar_{x}", "value": h})
    return bars


def extract_line_chart(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Detect lines (axes, possible trends)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
    points = []
    if lines is not None:
        for l in lines:
            x1, y1, x2, y2 = l[0]
            points.append({"x1": int(x1), "y1": int(y1), "x2": int(x2), "y2": int(y2)})
    return points


def extract_pie_chart(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 5)

    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 50,
                               param1=100, param2=30, minRadius=50, maxRadius=500)
    slices = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        # For simplicity, report circle existence
        slices.append({"circle_count": len(circles[0])})
    return slices


def extract_scatter_plot(image_np):
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    detector = cv2.SimpleBlobDetector_create()
    keypoints = detector.detect(gray)

    points = []
    for kp in keypoints:
        points.append({"x": int(kp.pt[0]), "y": int(kp.pt[1]), "size": kp.size})
    return points

# -------------------------------
# STEP 4: Main Pipeline
# -------------------------------
def extract_charts_from_pdf(pdf_path, output_json="chart_data.json", model_path="yolov5_charts.pt"):
    pages = pdf_to_images(pdf_path)
    model = load_yolo(model_path)

    results = {"pages": []}

    for page_idx, page_img in enumerate(pages, start=1):
        page_results = []

        # Convert PIL → np array
        img_np = np.array(page_img)

        # Detect charts
        results = model(img_np)
        det_df = results[0].boxes.data.cpu().numpy()  # [x1, y1, x2, y2, conf, cls]


        for _, row in det_df.iterrows():
            x1, y1, x2, y2, conf, cls, name = row
            chart_crop = img_np[int(y1):int(y2), int(x1):int(x2)]

            chart_data = []
            chart_type = name

            if chart_type == "bar":
                chart_data = extract_bar_chart(chart_crop)
            elif chart_type == "line":
                chart_data = extract_line_chart(chart_crop)
            elif chart_type == "pie":
                chart_data = extract_pie_chart(chart_crop)
            elif chart_type == "scatter":
                chart_data = extract_scatter_plot(chart_crop)

            page_results.append({
                "chart_type": chart_type,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "data": chart_data
            })

        results["pages"].append({"page_number": page_idx, "charts": page_results})

    # Save JSON
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"✅ Extraction complete. Saved to {output_json}")


# -------------------------------
# USAGE
# -------------------------------
if __name__ == "__main__":
    pdf_path = "C:/Users/binit/Downloads/[Fund Factsheet - May]360ONE-MF-May 2025.pdf.pdf"
    output_json = "charts_extracted.json"
    extract_charts_from_pdf(pdf_path, output_json, model_path="yolov5_charts.pt")
