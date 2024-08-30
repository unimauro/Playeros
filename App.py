from flask import Flask, render_template, request, send_file, redirect, url_for, send_from_directory
from PIL import Image
import requests
import io
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image = request.files['image']
        image_path = os.path.join('uploads', image.filename)
        image.save(image_path)
        stability_api_key = os.getenv('STABILITY_API_KEY')
        
        response = requests.post(
            f"https://api.stability.ai/v2beta/stable-image/generate/ultra",
            headers={
                "authorization": f"Bearer {stability_api_key}",
                "accept": "image/*"
            },
            files={'image': open(image_path, 'rb')},
            data={
                "prompt": "A close-up view of a person men or woman depend about the image uploaded standing on a tranquil beach, facing away from the camera. Only the shoulder and head of the person are visible, with the person wearing a white hat. The serene ocean stretches out before them, reflecting the calm, clear sky of a bright day. The waves gently lap at the shore, and the sun casts a soft glow on the water. The focus is on the peaceful scene, with the person quietly gazing out at the horizon.",
                "aspect_ratio": "16:9",
                "model":"sd3-turbo",
                "mode": "image-to-image",
                "strength": "0.7"
            },
        )
        
        if response.status_code == 200:
            # Guardar la imagen sin redimensionarla
            output_path = os.path.join('outputs', 'transformed_image.png')
            with open(output_path, 'wb') as file:
                file.write(response.content)

            return redirect(url_for('display_image', filename='transformed_image.png'))
        else:
            print("Error response:", response.status_code, response.text)
            return f"Error processing the image: {response.status_code} - {response.text}", 500

    return '''
    <!doctype html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <title>Playita</title>
    </head>
     <body>
        <div class="container d-flex align-items-center justify-content-center" style="min-height: 200vh;">
            <div class="card" style="width: 36rem; max-width: 100%;">
              <h1>Sube tu foto</h1>
              <form method=post enctype=multipart/form-data>
                <input type=file name=image>
                <input type=submit value=Subir>
              </form>
            </div>
        </div>
     </body>
    '''

@app.route('/display/<filename>')
def display_image(filename):
    return f'''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <title>Playita</title>
    </head>
    <body>
        <div class="container d-flex align-items-center justify-content-center" style="min-height: 200vh;">
            <div class="card" style="width: 36rem; max-width: 100%;">
                <img src="/outputs/{filename}" class="card-img-top w-100" alt="La Playita que Mereces" style="height: auto;">
                <div class="card-body">
                    <h5 class="card-title">Disfruta la playa</h5>
                    <p class="card-text">Here is your transformed image inside a Bootstrap card.</p>
                    <a href="/" class="btn btn-primary">Subir otra Imagen</a>
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# Ruta para servir archivos estáticos desde la carpeta outputs
@app.route('/outputs/<filename>')
def send_output_file(filename):
    return send_from_directory('outputs', filename)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    app.run(debug=True)
