import face_rec

def extractFaces(source_image):
    extracted_faces = []
    rgb_image = source_image[:, :, ::-1]

    # Detect face locations in the frame
    face_locations = face_recognition.face_locations(rgb_image)
