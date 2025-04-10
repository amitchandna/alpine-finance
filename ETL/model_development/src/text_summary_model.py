import tensorflow as tf
from shared_utils.connection_management import ConnectionManager
import tensorflow_hub as hub
import numpy as np


def training_data_collection():
    db = ConnectionManager()
    with open("../sql/training_data.sql", "r") as sql:
        sql_query = sql.read()
        training_data = db.query_data(sql_template=sql_query, params={})
    return str(training_data.decode("utf-8"))


def similarity_matrix(embed, messages):
    """Compute similarity matrix between sentences."""
    embed_messages = embed(messages)
    return tf.matmul(embed_messages, embed_messages, transpose_b=True)


def textrank_summarization(similarity_matrix_op, num_sentences=2):
    """Apply TextRank algorithm for summarization."""
    scores = tf.linalg.tensor_diag_part(similarity_matrix_op)
    top_indices = tf.argsort(scores, direction="DESCENDING")[:num_sentences]
    return top_indices


def summarize_text(embed, text):
    """Summarize a block of text using TextRank algorithm."""
    sentences = tf.strings.split(text, sep=". ")
    sentences_np = sentences.numpy()

    similarity_matrix_op = similarity_matrix(embed, sentences_np)
    summarized_indices = textrank_summarization(similarity_matrix_op, num_sentences=2)
    summarized_sentences = tf.gather(sentences, summarized_indices).numpy()
    summary = ". ".join(summarized_sentences.flatten().tolist())

    return summary


def main():
    """Main function to summarize text data from a database."""
    try:
        # Initialize TensorFlow Hub module for text embedding
        embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/5")

        # Fetch text data from the database
        text_data = training_data_collection()

        # Summarize each text entry
        summaries = [summarize_text(embed, text) for text in text_data]

        # Print the summaries
        for i, summary in enumerate(summaries):
            print(f"Summary {i + 1}: {summary}")

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    # Example database path and table name
    main()
