from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configurations for file uploads
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Retrieve the OpenAI API key from the environment variable
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


# Helper function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


def get_recommendations(event_type, subject_type):
    if event_type == 1:  # Outdoor
        if subject_type == 1:  # Butterfly
            aperture = "f/2.8 to f/4"
            shutter_speed = "1/1000s"
            iso = "100 to 400"
            explanation = (
                "Use a wide aperture (f/2.8 to f/4) for a shallow depth of field to blur the background and isolate the butterfly. "
                "A fast shutter speed (1/1000s) ensures the butterfly's movement is frozen, with ISO adjusted to light conditions."
            )
            rating = 4.5
        elif subject_type == 2:  # Landscape
            aperture = "f/8 to f/11"
            shutter_speed = "1/125s"
            iso = "100"
            explanation = (
                "For landscape photography, a narrower aperture (f/8 to f/11) ensures a larger depth of field, capturing sharp detail from foreground to background."
            )
            rating = 4.5
        elif subject_type == 3:  # Running Water
            aperture = "f/16"
            shutter_speed = "1/2s to 1/10s"
            iso = "100"
            explanation = (
                "To capture silky smooth water movement, use a narrow aperture (f/16) and a slow shutter speed (1/2s to 1/10s). "
                "Use a tripod for stability."
            )
            rating = 4.5
        elif subject_type == 4:  # Wildlife
            aperture = "f/5.6"
            shutter_speed = "1/1000s"
            iso = "400 to 800"
            explanation = (
                "For wildlife, a moderate aperture (f/5.6) with a fast shutter speed (1/1000s) helps freeze motion, especially in fast-moving animals. "
                "Increase ISO as needed for lighting."
            )
            rating = 4.5
        elif subject_type == 5:  # Street Photography
            aperture = "f/8"
            shutter_speed = "1/250s"
            iso = "200 to 400"
            explanation = (
                "A moderate aperture (f/8) ensures sufficient depth of field in street scenes, while a shutter speed of 1/250s captures candid moments."
            )
            rating = 4.5
        elif subject_type == 6:  # Events (Festivals, Concerts)
            aperture = "f/2.8 to f/4"
            shutter_speed = "1/250s"
            iso = "800 to 1600"
            explanation = (
                "A wide aperture (f/2.8 to f/4) is key for low-light event scenarios. A fast shutter speed (1/250s) freezes motion, while ISO is raised to manage light."
            )
            rating = 4.5

    elif event_type == 2:  # Indoor
        if subject_type == 7:  # Indoor Portrait
            aperture = "f/2.8 to f/4"
            shutter_speed = "1/125s"
            iso = "400 to 800"
            explanation = (
                "Use a wide aperture (f/2.8 to f/4) to achieve shallow depth of field, drawing focus to the subject. "
                "A shutter speed of 1/125s prevents motion blur, while ISO adjusts to indoor light."
            )
            rating = 4.5
        elif subject_type == 8:  # Indoor Landscape
            aperture = "f/11"
            shutter_speed = "1/60s"
            iso = "400"
            explanation = (
                "A narrow aperture (f/11) for an indoor landscape ensures greater depth of field, with a slow shutter speed of 1/60s and ISO 400 for adequate exposure."
            )
            rating = 4.5
        elif subject_type == 9:  # Indoor Action
            aperture = "f/2.8"
            shutter_speed = "1/500s or faster"
            iso = "1600 to 3200"
            explanation = (
                "For indoor action, a fast shutter speed (1/500s or faster) is essential to freeze movement, with a wide aperture and high ISO to compensate for low light."
            )
            rating = 4.5
        elif subject_type == 10:  # Product Photography
            aperture = "f/8 to f/11"
            shutter_speed = "1/125s"
            iso = "100 to 200"
            explanation = (
                "A moderate aperture (f/8 to f/11) ensures product details are sharp and in focus. A standard shutter speed of 1/125s is sufficient with controlled lighting."
            )
            rating = 4.5
        elif subject_type == 11:  # Low Light Situations
            aperture = "f/1.8 to f/2.8"
            shutter_speed = "1/60s or slower"
            iso = "1600 to 3200"
            explanation = (
                "In low light, use the widest aperture (f/1.8 to f/2.8) and slower shutter speed (1/60s or slower) to gather more light. Increase ISO to 1600 or 3200 as needed."
            )
            rating = 4.5

    return aperture, shutter_speed, iso, explanation, rating


# AI-based recommendations logic
import openai

def ai_recommendations(image_path):
    # Load your OpenAI API key from environment variables
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Create a prompt for the OpenAI model
    prompt = f"Analyze the image at '{image_path}' and provide photography recommendations including camera settings like aperture, shutter speed, ISO, white balance, and focus mode."

    try:
        # Call the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can use "gpt-4" if you have access
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract the AI's response
        recommendations = response.choices[0].message['content']

        # Process the recommendations if needed
        # This could involve parsing the response into structured data
        camera_tips, exposure_tips = parse_recommendations(recommendations)

        return camera_tips, exposure_tips

    except Exception as e:
        print(f"An error occurred while calling OpenAI API: {e}")
        return "Error generating recommendations", {}


# Home route with existing recommendations
@app.route("/", methods=["GET", "POST"])
def index():
    recommendation = {}
    uploaded_file_url = None
    if request.method == "POST":
        if 'event_type' in request.form and 'subject_type' in request.form:
            event_type = int(request.form["event_type"])
            subject_type = int(request.form["subject_type"])
            aperture, shutter_speed, iso, explanation, rating = get_recommendations(event_type, subject_type)
            recommendation = {
                "Aperture": aperture,
                "Shutter Speed": shutter_speed,
                "ISO": iso,
                "Explanation": explanation,
                "Rating": rating
            }
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                uploaded_file_url = url_for('static', filename=f'uploads/{filename}')
    return render_template("index.html", recommendation=recommendation, uploaded_file_url=uploaded_file_url)


# AI Shot Advisor route
@app.route("/ai_advisor", methods=["GET", "POST"])
def ai_advisor():
    camera_tips = ""
    exposure_tips = {}
    image_path = ""
    error_message = None  # Ensure error_message is initialized

    if request.method == "POST":
        if 'image' not in request.files:
            error_message = "No image file selected."
            return render_template("ai_advisor.html", image_path=image_path, camera_tips=camera_tips, exposure_tips=exposure_tips, error_message=error_message)
        
        file = request.files['image']
        if file.filename == '':
            error_message = "No file was uploaded."
            return render_template("ai_advisor.html", image_path=image_path, camera_tips=camera_tips, exposure_tips=exposure_tips, error_message=error_message)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(image_path)
            
            # Call AI function for recommendations
            camera_tips, exposure_tips = ai_recommendations(image_path)
    
    return render_template("ai_advisor.html", image_path=image_path, camera_tips=camera_tips, exposure_tips=exposure_tips, error_message=error_message)


if __name__ == "__main__":
    app.run(debug=True)
