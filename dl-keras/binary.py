# -*- coding: utf-8 -*-
from keras import layers, models
from keras.datasets import imdb
import numpy as np

# 二値分類

(train_data, train_labels), (test_data, test_labels) = \
    imdb.load_data(num_words=10000)

# 2次元テンソルへのデータ変換(次元数＝ラベル数）


def vectorize_sequences(sequences, dimension=10000):
    # len(sequences) * dimension の　0埋め行列を作成
    results = np.zeros((len(sequences), dimension))

    #
    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.

    return results


x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)

# ラベルもベクトル化しておく
y_train = np.array(train_labels).astype('float32')
y_test = np.array(test_labels).astype('float32')

model = models.Sequential()
model.add(layers.Dense(16, activation='relu', input_shape=(10000,)))
model.add(layers.Dense(16, activation='relu'))
model.add(layers.Dense(1, activation='sigmoid'))

model.compile(optimizer='rmsprop', loss='binary_crossentropy',
              metrics=['accuracy'])

# 検証データセットの設定
x_val = x_train[:10000]
partial_x_train = x_train[10000:]

y_val = y_train[:10000]
partial_y_train = y_train[10000:]

# history = model.fit(
#     partial_x_train,
#     partial_y_train,
#     epochs=20,
#     batch_size=512,
#     validation_data=(x_val, y_val))

history = model.fit(
    x_train,
    y_train,
    epochs=20,
    batch_size=512,
    validation_data=(x_val, y_val))


# history.historyは訓練中の履歴データを保持
history_dict = history.history
print(history_dict.keys())

# 正解率
results = model.evaluate(x_test, y_test)
print(results)
