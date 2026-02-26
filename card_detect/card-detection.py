import cv2
import numpy as np
import pytesseract
import difflib

# Path to Tesseract OCR executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Keywords to match
keywords = [
    # Card brands
    "topps", "panini", "leaf", "upper deck", "donruss",
    # Sports terms
    "outfield", "pitcher", "catcher", "infield", "batter", "center fielder",
    "hitter", "closer",
    # MLB teams
    "diamondbacks", "athletics", "braves", "orioles", "red sox", "cubs",
    "white sox", "reds", "guardians", "rockies", "tigers", "astros", "royals",
    "angels", "dodgers", "marlins", "brewers", "twins", "mets", "yankees",
    "phillies", "pirates", "padres", "giants", "mariners", "cardinals", "rays",
    "rangers", "blue jays", "nationals",
    # General
    "rookie", "baseball", "mlb", "prospects", "chrome",
]

# Load image and create copy
image = cv2.imread("card.png")
original_image = image.copy()

# Detect card edges
grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(grayscale, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)

cv2.imshow("Edges", edges)
cv2.waitKey(0)

contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL,
                               cv2.CHAIN_APPROX_SIMPLE)
largest = max(contours, key=cv2.contourArea)
peri = cv2.arcLength(largest, True)
approx = cv2.approxPolyDP(largest, 0.02 * peri, True)
cv2.drawContours(image, [approx], -1, (0, 255, 0), 3)

cv2.imshow("Detected Card", image)
cv2.waitKey(0)


# Warp card to rectangle
def order_points(pts):
    pts = pts.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


rect = order_points(approx)
width, height = 300, 420
dst = np.array([
    [0, 0],
    [width - 1, 0],
    [width - 1, height - 1],
    [0, height - 1]
], dtype="float32")

M = cv2.getPerspectiveTransform(rect, dst)
warp = cv2.warpPerspective(original_image, M, (width, height))

cv2.imshow("Card", warp)
cv2.imwrite("card_extracted.jpg", warp)
cv2.waitKey(0)

all_detected_text = []

# OCR on top region (brand name)
top_region = warp[0:50, 0:300]
top_gray = cv2.cvtColor(top_region, cv2.COLOR_BGR2GRAY)
top_thresh = cv2.threshold(top_gray, 0, 255,
                           cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
top_resized = cv2.resize(top_thresh, None, fx=3, fy=3,
                         interpolation=cv2.INTER_CUBIC)

cv2.imshow("Top Region", top_region)
cv2.waitKey(0)
cv2.imshow("Top Preprocessed", top_resized)
cv2.waitKey(0)

top_text = pytesseract.image_to_string(top_resized,
                                       config=r'--oem 3 --psm 6')
top_text_clean = top_text.lower().replace("\n", " ").strip()
print("Top region text:", top_text_clean)
all_detected_text.append(top_text_clean)

# OCR on bottom region (keywords, team)
bottom_region = warp[300:420, 0:300]
gray_bottom = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
gray_bottom = cv2.convertScaleAbs(gray_bottom, alpha=1.3, beta=10)
thresh_bottom = cv2.threshold(gray_bottom, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
bottom_resized = cv2.resize(thresh_bottom, None, fx=3, fy=3,
                            interpolation=cv2.INTER_CUBIC)

cv2.imshow("Bottom Region", bottom_region)
cv2.waitKey(0)
cv2.imshow("Bottom Preprocessed", bottom_resized)
cv2.waitKey(0)

bottom_text = pytesseract.image_to_string(bottom_resized,
                                          config=r'--oem 3 --psm 6')
bottom_text_clean = bottom_text.lower().replace("\n", " ").strip()
print("Bottom region text:", bottom_text_clean)
all_detected_text.append(bottom_text_clean)

# OCR on FULL card
full_gray = cv2.cvtColor(warp, cv2.COLOR_BGR2GRAY)
full_thresh = cv2.threshold(full_gray, 0, 255,
                            cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
full_resized = cv2.resize(full_thresh, None, fx=2, fy=2,
                          interpolation=cv2.INTER_CUBIC)

cv2.imshow("Full Card Preprocessed", full_resized)
cv2.waitKey(0)

full_text = pytesseract.image_to_string(full_resized,
                                        config=r'--oem 3 --psm 6')
full_text_clean = full_text.lower().replace("\n", " ").strip()
print("Full card text:", full_text_clean)
all_detected_text.append(full_text_clean)

# Combine all detected text
all_text = " ".join(all_detected_text)
print("\nAll detected text:", all_text)

# Fuzzy matching to detect card
ocr_words = all_text.split()
matched_keywords = []

for word in ocr_words:
    matches = difflib.get_close_matches(word, keywords, cutoff=0.6)
    if matches:
        matched_keywords.append((word, matches[0]))

if matched_keywords:
    print("\nIt's a sports card!")
    print("Matched keywords:")
    for ocr_word, keyword in matched_keywords:
        print(f"  '{ocr_word}' → '{keyword}'")
else:
    print("\nNot a sports card / unknown card type")

cv2.destroyAllWindows()
