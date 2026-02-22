import os
from flask import request, current_app, render_template
from repositories.rabbit_mq import RabbitMQQueue

queue = RabbitMQQueue()

class DataCollector:
    def collect_user_data(self):
        file = request.files.get("user_input")
        if not file or file.filename == '':
            return "<h1>Error: No file selected!</h1>", 400

        filename = file.filename
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        queue.publish_job({
            'filepath': filepath,
            'filename': filename,
        })

        return render_template("uploaded_data.html")
