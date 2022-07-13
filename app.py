from flask import Flask, request
import flask
from summarizators import Summarizator
import sqlalchemy as db2
from datetime import datetime
import ast

app = Flask(__name__, template_folder='web')
app.static_folder = 'static'
app.config['MAX_CONTENT_LENGTH'] = 4 * 1024
engine = Summarizator()

db_engine = db2.create_engine('sqlite:///database/summary.db', connect_args={'check_same_thread': False})
metadata = db2.MetaData()

summarization_table = db2.Table('Summarization', metadata, autoload=True, autoload_with=db_engine)
summary_table = db2.Table('Summary', metadata, autoload=True, autoload_with=db_engine)
text_table = db2.Table('Text', metadata, autoload=True, autoload_with=db_engine)


# this function is needed because it is possible that in future extensions we will not need some texts to be inserted
def insert_row(table, connection, **kwargs):
    query = db2.insert(table).values(**kwargs)
    result_proxy = connection.execute(query)
    row_pk = result_proxy.inserted_primary_key[0]
    return row_pk


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] == 'txt'


@app.route('/')
def index():
    return flask.render_template('index.html', summary_type='extractive', result_id=0)


@app.route('/summarize', methods=['POST'])
def summarize():
    user_data = request.form.to_dict()
    text = user_data['user_text']
    summary_type = user_data['summary_type']
    length_parameter = user_data['length_parameter']  # number of sentences (extractive) or length regularizator fot NN

    summary = ''  # empty summary at the start
    result_id = 0  # will be modified after summarization event, otherwise it blocks the evaluation module
    if len(text) > 0:  # if user passed something
        connection = db_engine.connect()

        text_sentences, text_words = engine.get_stats(text)

        start = datetime.now()
        if summary_type == 'header':
            summary += engine.generate_header(text, float(length_parameter))
        elif summary_type == 'abstractive':
            summary += engine.generate_abstractive_summary(text, float(length_parameter))
        elif summary_type == 'extractive':
            summary += engine.generate_extractive_summary(text, int(length_parameter))
        else:
            raise NotImplementedError
        end = datetime.now()

        duration = (end - start).total_seconds()  # duration of summarization event
        summary_sentences, summary_words = engine.get_stats(summary)

        text_id = insert_row(text_table, connection,
                             n_sentences=text_sentences, n_words=text_words, text=text)
        summary_id = insert_row(summary_table, connection,
                                n_sentences=summary_sentences, n_words=summary_words, text=summary,
                                kind=summary_type, length_parameter=float(length_parameter))
        # result id is needed to connect summarization event and rating
        result_id = insert_row(summarization_table, connection,
                               text_id=text_id, summary_id=summary_id, datetime=end, duration=duration)

        connection.close()

    return flask.render_template(
        'index.html', user_text=text, summary=summary, summary_type=summary_type, result_id=result_id
    )


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file and allowed_file(file.filename):
        text = file.read().decode("utf-8")
        return flask.render_template('index.html', user_text=text, summary_type='extractive', result_id=0)
    else:
        return flask.render_template('index.html', user_text='Incorrect file format', summary_type='extractive')


@app.route('/evaluate', methods=['POST'])
def evaluate():
    user_data = request.form.to_dict()
    mark_data = user_data['summary_mark']
    mark_data = ast.literal_eval(mark_data)
    mark = mark_data['mark']
    result_id = mark_data['id']

    connection = db_engine.connect()

    # getting summary
    query = db2.select(
        [summary_table.columns.text, summary_table.columns.kind, summarization_table.columns.summary_id]
    ).select_from(
        summarization_table.join(summary_table, summary_table.columns.id == summarization_table.columns.summary_id)
    ).where(summarization_table.columns.id == result_id)
    summary, summary_type, _ = connection.execute(query).fetchall()[0]

    # getting user text
    query = db2.select(
        [text_table.columns.text, summarization_table.columns.text_id]
    ).select_from(
        summarization_table.join(text_table, text_table.columns.id == summarization_table.columns.summary_id)
    ).where(summarization_table.columns.id == result_id)
    text, _ = connection.execute(query).fetchall()[0]

    # inserting summary mark
    query = db2.update(summarization_table).values(rating=mark).where(summarization_table.columns.id == result_id)
    connection.execute(query)

    connection.close()

    return flask.render_template('index.html', summary=summary, user_text=text, result_id=0, summary_type=summary_type)


if __name__ == '__main__':
    app.run(debug=True)
