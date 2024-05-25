from model import extract_signatures_from_documents
from model import text_output_signatures
from model import visualize_best_signatures
from flask import Flask, request, jsonify
import traceback
import base64
from io import BytesIO
from PIL import Image
import gradio as gr
import subprocess
import socket
import threading

app = Flask(__name__)

docs_path = 'Docs'
predicts_path = 'Predicts'
employee_signs_path = 'Signatures/' 
predicts_signs_path = 'Predicts/Signs'


@app.route('/process_signature', methods=['POST'])
def handle_photo():
    try:
        # Принимаем данные в формате JSON
        data = request.get_json()
        print(data)
        img_base64 = data['img']
        employee_name = data['employee_name']

        # Декодируем изображение из Base64
        img_data = base64.b64decode(img_base64)
        img = Image.open(BytesIO(img_data))
        img.save("Docs/photo.jpg")  # Сохраняем изображение

        # Обрабатываем документ
        res_extract = extract_signatures_from_documents(docs_path, predicts_signs_path)
        text_output = text_output_signatures(employee_name, employee_signs_path+employee_name, predicts_signs_path) 
       
        images_paths = visualize_best_signatures(employee_signs_path + employee_name, predicts_signs_path) 
        imagesbase64 = images_to_base64_list(images_paths)

        # Создаем ответ
        response = {
            "extraction_result": res_extract,
            "text_output": text_output,
            "img_paths": imagesbase64
        }
        return jsonify(response)
    except Exception as e:
        traceback.print_exc()
        #return jsonify({"error": "bad"}), 500
        return jsonify({"error": str(e)}), 500
    

def images_to_base64_list(output_images):
    base64_images = []
    for image_path in output_images:
        # Читаем изображение в режиме двоичного файла
        with open(image_path, "rb") as image_file:
            # Кодируем содержимое файла в строку base64
            base64_string = base64.b64encode(image_file.read()).decode('utf-8')
            base64_images.append(base64_string)
    return base64_images


def process_image(img, employee_name):
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    data = {
        "img": img_str,
        "employee_name": employee_name
    }

    response = app.test_client().post('/process_signature', json=data)
    result = response.get_json()

    if 'error' in result:
        return result['error']
    else:
        return result['text_output'], [Image.open(BytesIO(base64.b64decode(img))) for img in result['img_paths']]

iface = gr.Interface(
    fn=process_image,
    inputs=[gr.Image(type="pil"), gr.Textbox(label="Employee Name")],
    outputs=[gr.Textbox(label="Extraction Result"), gr.Gallery(label="Signatures")]
)


def run_flask():
    app.run(host='0.0.0.0', port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    iface.launch(server_name="0.0.0.0", server_port=7860, share=True)

# def find_free_port():
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#         s.bind(('', 0))
#         return s.getsockname()[1]

# if __name__ == '__main__':
#     # Запускаем Flask в фоновом режиме
#     flask_process = subprocess.Popen(["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"])

#     # Запускаем Gradio интерфейс на свободном порту
#     free_port = find_free_port()
#     iface.launch(server_name="0.0.0.0", server_port=free_port, share=True)

#     # Ожидаем завершения процесса Flask
#     # flask_process.wait()