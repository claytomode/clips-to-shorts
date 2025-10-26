import cv2

def get_rois(video_path):
    """
    Opens a UI for the user to select webcam and gameplay ROIs (Regions of Interest).
    Returns coordinates in (x1, y1, x2, y2) format.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError("Cannot open video file")

    ret, frame = cap.read()
    if not ret:
        raise IOError("Cannot read first frame of video")
    
    cap.release()
    cv2.destroyAllWindows()
    
    def convert_roi_format(roi):
        x, y, w, h = roi
        return (x, y, x + w, y + h)

    print("\n--- INSTRUCTIONS ---")
    print("A window will open. Click and drag to select the WEBCAM.")
    print("Press ENTER or SPACE to confirm.")
    print("Press 'c' to cancel.")
    
    webcam_roi = cv2.selectROI("Select WEBCAM Region (then press Enter)", frame)
    if not any(webcam_roi):
        raise SystemExit("Selection cancelled. Exiting.")
    webcam_coords = convert_roi_format(webcam_roi)
    
    print("\n--- INSTRUCTIONS ---")
    print("Select the GAMEPLAY region.")
    print("Press ENTER or SPACE to confirm.")
    
    gameplay_roi = cv2.selectROI("Select GAMEPLAY Region (then press Enter)", frame)
    if not any(gameplay_roi):
        raise SystemExit("Selection cancelled. Exiting.")
    gameplay_coords = convert_roi_format(gameplay_roi)

    cv2.destroyAllWindows()
    
    return webcam_coords, gameplay_coords