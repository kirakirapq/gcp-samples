# -*- coding: utf-8 -*-
from keras import layers, models
from keras.datasets import reuters
import numpy as np
import sys

# 多クラス多ラベル分類
# 出現頻度が高い10,000個の単語を抽出
(train_data, train_labels), (test_data, test_labels) = \
    reuters.load_data(num_words=10000)

# 訓練データ数：8892
print(len(train_data))

# テストサンプル数：2246
print(len(test_data))

# データの確認 [1, 386, 234, 5, 299, 100, ...] 単語（train_labels）のインデックスのリストになっている
print(train_data[15])

# ラベルの確認: [3, 8, 23, 45]
# ラベルは0 - 45までの数字が入っている
# この数字はreuters.get_word_index()のデータに紐づいている
print(train_labels)

# 2次元テンソルへのデータ変換(次元数＝ラベル数）


def vectorize_sequences(sequences, dimension=10000):
    # len(sequences) * dimension の　0埋め行列を作成
    results = np.zeros((len(sequences), dimension))

    for i, sequence in enumerate(sequences):
        results[i, sequence] = 1.

    return results


x_train = vectorize_sequences(train_data)
x_test = vectorize_sequences(test_data)


# one-hotエンコーディング
def to_one_hot(labels, dimension=46):
    results = np.zeros((len(labels), dimension))
    for i, label in enumerate(labels):
        results[i, label] = 1.

    return results


one_hot_train_labels = to_one_hot(train_labels)
one_hot_test_labels = to_one_hot(test_labels)

model = models.Sequential()
model.add(layers.Dense(64, activation='relu', input_shape=(10000,)))
model.add(layers.Dense(64, activation='relu'))
model.add(layers.Dense(46, activation='softmax'))

model.compile(optimizer='rmsprop', loss='categorical_crossentropy',
              metrics=['accuracy'])

# 検証データセットの設定
x_val = x_train[:1000]
partial_x_train = x_train[1000:]

y_val = one_hot_train_labels[:1000]
partial_y_train = one_hot_train_labels[1000:]

history = model.fit(
    partial_x_train,
    partial_y_train,
    epochs=20,
    batch_size=512,
    validation_data=(x_val, y_val))

loss = history.history['loss']
val_loss = history.history['val_loss']
