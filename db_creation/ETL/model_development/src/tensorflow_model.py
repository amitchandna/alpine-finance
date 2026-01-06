"""This is a set of code that was provided by Hands on ML and the NLP chapter has an RNN model that was applied to
section 1 data from the 10k values in the db"""
import tensorflow as tf
from shared_utils.connection_management import ConnectionManager


def training_data_collection():
    db = ConnectionManager()
    with open("../sql/training_data.sql", "r") as sql:
        sql_query = sql.read()
        training_data = db.query_data(sql_template=sql_query, params={})
    return str(training_data)


def encode_data(data):
    text_vec_layer = tf.keras.layers.TextVectorization(standardize="lower")
    text_vec_layer.adapt([data])
    encoded = text_vec_layer([data])[0]
    encoded -= 2
    n_tokens = text_vec_layer.vocabulary_size() - 2
    dataset_size = len(encoded)
    print(n_tokens, dataset_size)
    return encoded, n_tokens


def to_dataset(sequence, length, shuffle=False, seed=None, batch_size=32):
    ds = tf.data.Dataset.from_tensor_slices(sequence)
    ds = ds.window(length + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda window_ds: window_ds.batch(length + 1))
    if shuffle:
        ds = ds.shuffle(buffer_size=100_000, seed=seed)
    ds = ds.batch(batch_size)
    return ds.map(lambda window: (window[:, :-1], window[:, 1:])).prefetch(1)


def prepare_datasets(encoded, length=100, seed_value=42):
    tf.random.set_seed(seed_value)
    train_set = to_dataset(encoded[:16_000_000], length=length, shuffle=True, seed=42)
    valid_set = to_dataset(encoded[16_000_000:17_000_000], length=length)
    test_set = to_dataset(encoded[17_000_000:], length=length)
    return train_set, valid_set, test_set


def build_plus_train_char_rnn_model(n_tokens, train_set, valid_set):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Embedding(input_dim=n_tokens, output_dim=16),
            tf.keras.layers.GRU(128, return_sequences=True),
            tf.keras.layers.Dense(n_tokens, activation="softmax"),
        ]
    )
    model.compile(
        loss="sparse_categorical_crossentropy", optimizer="nadam", metrics=["accuracy"]
    )
    model_ckpt = tf.keras.callbacks.ModelCheckpoint(
        "my_section_one_model.keras", monitor="val_accuracy", save_best_only=True
    )
    history = model.fit(
        train_set, validation_data=valid_set, epochs=10, callbacks=[model_ckpt]
    )


dataset = training_data_collection()
encoding, n_tokens = encode_data(dataset)
training, valid, testing = prepare_datasets(encoded=encoding)
build_plus_train_char_rnn_model(train_set=training, valid_set=valid, n_tokens=n_tokens)
