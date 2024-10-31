import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os


# Function to capture an image from the camera and save it
def capture_image(filename="captured_image.jpg"):
    # Open a connection to the camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    # Allow the camera to warm up
    cv2.waitKey(1000)

    # Capture a single frame
    ret, frame = cap.read()

    # Release the camera
    cap.release()

    if ret:
        # Save the captured frame
        cv2.imwrite(filename, frame)
        print(f"Image saved as {filename}")
        return filename
    else:
        print("Error: Could not read frame.")
        return None


# Function to detect and extract face from an image
def extract_face(image_path, face_cascade_path="haarcascade_frontalface_default.xml"):
    face_cascade = cv2.CascadeClassifier(face_cascade_path)
    image = cv2.imread(image_path)

    if image is None:
        print(f"Error: Could not load image {image_path}")
        return None

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    if len(faces) == 0:
        print("Error: No face detected in image {image_path}")
        return None

    # Assuming only one face per image for simplicity
    x, y, w, h = faces[0]
    face = gray[y : y + h, x : x + w]
    return face


# Function to compare two images
def compare_images(image1_path, image2_path):
    # Extract faces from the images
    face1 = extract_face(image1_path)
    face2 = extract_face(image2_path)

    if face1 is None or face2 is None:
        print("Error: One of the images could not be loaded or no face detected.")
        return None

    # Resize the faces to the same size (if necessary)
    face2 = cv2.resize(face2, (face1.shape[1], face1.shape[0]))

    # Compute the Structural Similarity Index (SSI)
    score, diff = ssim(face1, face2, full=True)
    print(f"Similarity Score: {score}")

    return score


if __name__ == "__main__":
    # Capture an image from the camera
    captured_image_path = capture_image()

    if captured_image_path:
        # Path to the reference image
        reference_image_path = "my_image.jpg"

        # Ensure the Haar Cascade file is in the correct location
        haar_cascade_path = "haarcascade_frontalface_default.xml"
        if not os.path.exists(haar_cascade_path):
            print(f"Error: Haar Cascade file not found at {haar_cascade_path}")
        else:
            # Compare the captured image with the reference image
            similarity_score = compare_images(captured_image_path, reference_image_path)

            if similarity_score is not None and similarity_score >= 0.5:
                print("The faces match!")
            else:
                print("The faces do not match.")

            # Delete the captured image
            os.remove(captured_image_path)
            print(f"Deleted {captured_image_path}")
