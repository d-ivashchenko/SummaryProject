from flask import Flask, request
import flask
from summarizators import Summarizator

app = Flask(__name__, template_folder='web')
app.static_folder = 'static'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024
engine = Summarizator()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == 'txt'


@app.route('/')
def index():
    return flask.render_template('index.html', summary_type='extractive')


@app.route('/summarize', methods=['POST'])
def summarize():
    user_data = request.form.to_dict()
    text = user_data['user_text']
    summary_type = user_data['summary_type']

    summary = ''
    if summary_type == 'header':
        summary += engine.generate_header(text)
    elif summary_type == 'abstractive':
        summary += engine.generate_abstractive_summary(text)
    elif summary_type == 'extractive':
        summary += engine.generate_extractive_summary(text)
    else:
        raise NotImplementedError

    return flask.render_template('index.html', user_text=text, summary=summary, summary_type=summary_type)


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        text = file.read().decode("utf-8")
        return flask.render_template('index.html', user_text=text, summary_type='extractive')
    else:
        return flask.render_template('index.html', user_text='Incorrect file format', summary_type='extractive')


if __name__ == '__main__':
    app.run(debug=True)
