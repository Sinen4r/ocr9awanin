import cv2
def remove_watermark(path: str):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    # Ignore light gray (watermark), keep dark text
    _, mask = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return mask
def resize_from_bottom(img, new_height):
    img = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape[:2]
    print(h,w)
    if new_height >= h:
        return img  
    return img[:h - new_height, :]
cv2.imwrite("cleaned2s.png", remove_watermark("COCArabe/COCArabe_page-017.png"))

cv2.imwrite("cleaned2.png", resize_from_bottom("COCArabe/COCArabe_page-017.png", 150))

cv2.waitKey(0)
cv2.destroyAllWindows()