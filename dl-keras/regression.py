# -*- coding: utf-8 -*-
from keras import layers, models
from keras.datasets import boston_housing
import numpy as np

# 回帰問題

(train_data, train_targets), (test_data, test_targets) = \
    boston_housing.load_data()

# データ確認
print(train_data.shape)
# (400, 13)
print(train_targets)
# array([15.2, 42,3, 50., ....])

# データの正規化
mean = train_data.mean(axis=0)
train_data -= mean
std = train_data.std(axis=0)
train_data /= std

test_data -= mean
test_data /= std

# モデルを構築する関数


def build_model():
    model = models.Sequential()
    model.add(layers.Dense(64, activation='relu',
                           input_shape=(train_data.shape[1],)))

    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(1))
    model.compile(optimizer='rmsprop', loss='mse', metrics=['mae'])

    return model


# k分割交差検証
k = 4  # 分割数
num_val_samples = len(train_data) // k  # 切り捨て除算
num_epochs = 100
all_scores = []

for i in range(k):
    print('process fold #', i)

    # 検証データ
    val_data = \
        train_data[i * num_val_samples: num_val_samples * (i + 1)]
    val_targets = \
        train_targets[i * num_val_samples: num_val_samples * (i + 1)]

    # 訓練データ
    partial_train_data = np.concatenate(
        [
            train_data[:i*num_val_samples],
            train_data[(i + 1)*num_val_samples:]
        ],
        axis=0)

    partial_train_targets = np.concatenate(
        [
            train_targets[:i*num_val_samples],
            train_targets[(i + 1)*num_val_samples:]
        ],
        axis=0)

    # モデルを構築
    model = build_model()

    model.fit(
        partial_train_data,
        partial_train_targets,
        epochs=num_epochs,
        batch_size=1,
        verbose=0)

    # 評価値を取得
    val_mse, val_mae = model.evaluate(val_data, val_targets, verbose=0)
    all_scores.append(val_mae)

    # 平均絶対誤差 (MAE)
    print('平均絶対誤差 (MAE)')
    print(val_mae)

    # 平均二乗誤差 (MSE)
    print('平均二乗誤差(MSE)')
    print(all_scores)
    print(np.mean(all_scores))
