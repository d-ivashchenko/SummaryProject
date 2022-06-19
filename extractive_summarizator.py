import math
import numpy as np
from collections import Counter


class KLSummarizer:
    def __init__(self, sentence_tokenizer, word_tokenizer, lemmatizer, stop_words, punctuation):
        self.sentence_tokenizer = sentence_tokenizer
        self.word_tokenizer = word_tokenizer
        self.lemmatizer = lemmatizer

        self.stop_words = stop_words
        self.punctuation = punctuation

    def decompose(self, document):
        sentences = self.sentence_tokenizer(document)
        pretokenized_sentences = [self.word_tokenizer(sentence) for sentence in sentences]

        n_sentences = len(sentences)
        lemmatized_sentences = []
        for i in range(n_sentences):
            filtered_sentence = [word for word in pretokenized_sentences[i] if
                                 word not in self.stop_words and word not in self.punctuation]
            lemmatized_sentence = [self.lemmatizer.lemmatize(word) for word in filtered_sentence]
            lemmatized_sentences.append(lemmatized_sentence)

        return sentences, lemmatized_sentences

    def summarize(self, document, n_sentences):
        sentences, tokenized_sentences = self.decompose(document)
        document_size = len(sentences)
        summary_size = min(document_size, n_sentences)
        summary_sentences = self._kl_summary(sentences, tokenized_sentences, summary_size)
        return ' '.join(summary_sentences)

    def _calculate_TF(self, tokens):
        return dict(Counter(tokens))

    def _kl_summary(self, sentences, tokenized_sentences, n_sentences):
        sentences_copy = sentences.copy()
        rated_sentences_ids = []
        summary_tokens = []

        words = [token for sentence in tokenized_sentences for token in sentence]

        word_freq = self._calculate_TF(words)
        for key in word_freq.keys():
            word_freq[key] /= len(word_freq.keys())

        i = 0
        while len(tokenized_sentences) > 0 and i < n_sentences:
            kls = []

            for sentence in tokenized_sentences:
                joint_freq = self._calculate_joint_freq(sentence, summary_tokens)
                kls.append(self._kl_divergence(joint_freq, word_freq))

            min_index = kls.index(min(kls))
            summary_tokens = summary_tokens + tokenized_sentences[min_index]

            rated_sentences_ids.append(sentences.index(sentences_copy[min_index]))
            del tokenized_sentences[min_index]
            del sentences_copy[min_index]
            i += 1

        result = np.array(sentences)[sorted(rated_sentences_ids)]
        return result.tolist()

    def _calculate_joint_freq(self, word_list_1, word_list_2):
        total_length = len(word_list_1) + len(word_list_2)

        word_count1 = self._calculate_TF(word_list_1)
        word_count2 = self._calculate_TF(word_list_2)

        # inputs the counts from the first list
        joint = word_count1.copy()

        # adds in the counts of the second list
        for k in word_count2:
            if k in joint:
                joint[k] += word_count2[k]
            else:
                joint[k] = word_count2[k]

        # divides total counts by the combined length
        for k in joint:
            joint[k] /= float(total_length)

        return joint

    def _kl_divergence(self, summary_freq, doc_freq):
        sum_val = 0
        for w in summary_freq:
            frequency = doc_freq.get(w)
            if frequency:
                sum_val += frequency * math.log(frequency / summary_freq[w])

        return sum_val
