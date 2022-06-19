# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import pickle
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from extractive_summarizator import KLSummarizer

ABSTRACTIVE_SUMMARY_MODEL_FOLDER = 'abstractive_model'
HEADER_MODEL_FOLDER = 'header_model'


def whitespace_handler(string):
    return re.sub('\s+', ' ', re.sub('\n+', ' ', string.strip()))


class Summarizator:
    def __init__(
            self,
            header_folder=HEADER_MODEL_FOLDER,
            abstractive_folder=ABSTRACTIVE_SUMMARY_MODEL_FOLDER,
            handler=whitespace_handler
    ):
        self.header_summarizer = pickle.load(open(header_folder+'/model.pkl', 'rb'))
        self.header_tokenizer = pickle.load(open(header_folder+'/tokenizer.pkl', 'rb'))

        self.abstractive_summarizer = pickle.load(open(abstractive_folder + '/model.pkl', 'rb'))
        self.abstractive_tokenizer = pickle.load(open(abstractive_folder + '/tokenizer.pkl', 'rb'))

        self.whitespace_handler = handler

        nltk.download('stopwords')
        nltk.download('punkt')
        nltk.download('wordnet')
        nltk.download('omw-1.4')

    def generate_header(self, text):
        input_ids = self.header_tokenizer(
            [self.whitespace_handler(text)],
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )["input_ids"]

        output_ids = self.header_summarizer.generate(
            input_ids=input_ids,
            max_length=200,
            min_length=10,
            no_repeat_ngram_size=2,
            num_beams=4,
            length_penalty=1
        )[0]

        text_header = self.header_tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )

        return text_header

    def generate_abstractive_summary(self, text):
        preprocessed_text = self.whitespace_handler(text)
        prepared_text = "summarize: " + preprocessed_text

        input_ids = self.abstractive_tokenizer(
            prepared_text,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )["input_ids"]

        output_ids = self.abstractive_summarizer.generate(
            input_ids=input_ids,
            max_length=10000,
            min_length=100,
            no_repeat_ngram_size=2,
            num_beams=4,
            length_penalty=0.2
        )[0]

        abstractive_summary = self.abstractive_tokenizer.decode(
            output_ids,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

        return abstractive_summary

    def generate_extractive_summary(self, text):
        punctuation = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', ':', ';', '<', '=',
                       '>', '?', '@', '[', '\\', ']', '^', '_', '`', '{', '|', '}', '~']
        stop_words = stopwords.words('english')
        lemmatizer = WordNetLemmatizer()

        kl_summarizer = KLSummarizer(sent_tokenize, word_tokenize, lemmatizer, stop_words, punctuation)
        extractive_summary = kl_summarizer.summarize(text, 7)

        return extractive_summary

