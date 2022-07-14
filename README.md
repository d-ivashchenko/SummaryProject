# SummaryProject
Summarizator for Software Architecture course.

You can summarize texts with 3 different approaches using 3 different models:
- extractive summarization gives you a summary based on text sentences only
- abstractive summarization gives you a generated summary based on document content and external lexis
- to generate a short description of the text you can use header mode

## Setup
1. Download the repository on your local machine.
2. The project was created on Python 3.7, so using this version is strongly recommended. Install all the packages listed in the `requirements.txt` file.
3. Download archives `abstractive_model.rar` and `header_model.rar` from [here](https://drive.google.com/drive/folders/11VVTTNYCIeoabGCpzzoplFdCdsVDJ_sH?usp=sharing), unpack the archives and place the content in the `abstractive_model` and `header_model` folders correspondingly before running the project.

## Usage
To start the app, you need to run the script `app.py`. Then you need to wait up to 5 minutes before the models will be loaded and then you can go to http://127.0.0.1:5000/. 

You can enter text in the upper input or import your `.txt` file. Then, you can choose from 3 summarization mods. If you choose _extractive summary_ you can specify the desired length of summary (in sentences). If you choose _abstractive summary_ or _header_, then you can specify the length penalty. If you want longer summary, you need to move the slider to the right, otherwise - to the left. 

To start summarization, click "Summarize".

You can evaluate the quality of the summary from 1 to 5 after it was generated and click "Evaluate summary" to submit the score.

![image](https://user-images.githubusercontent.com/38154370/179032005-61f12197-4389-48b5-8b6d-81a0496ee99c.png)

## Database
There is a database to analyse some characteristics of summarization process, like duration, compression factor and quality of summarization. The database is stored in `database\summary.db` file. It can be accessed using `sqlite3`.

To re-initialise the database, run the script `database\database.py`
