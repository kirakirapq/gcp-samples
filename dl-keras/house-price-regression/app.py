# -*- coding: utf-8 -*-
from keras import layers, models
from pandas.core.frame import DataFrame
import numpy as np
import pandas as pd


def load_file(path: str) -> DataFrame:
    """CSVファイルをロード
    Args:
        path (str):
    Returns:
        DataFrame:
    """
    df = pd.read_csv(path, index_col=1)
    df = df.fillna(0)
    df.replace('NA', 0)
    df.replace('NaN', 0)

    return df


def normalization(data: DataFrame) -> DataFrame:
    """データを正規化する関数
    Args:
        data (DataFrame): 元のデータ
    Returns:
        DataFrame: 正規化されたデータ
    """
    mean = data.mean(axis=0)
    data -= mean
    std = data.std(axis=0)
    data /= std

    return data


def build_model():
    model = models.Sequential()
    model.add(layers.Dense(64, activation='relu',
                           input_shape=(train_data.shape[1],)))

    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(1))
    model.compile(optimizer='rmsprop', loss='mse', metrics=['mae'])

    return model


try:
    # train data
    df_train = load_file('./datasets/train.csv')
    # train_data = df_train.iloc[:,:-1]
    # 暫定的に数値のデータだけ使用する
    train_data_df_raw = df_train.iloc[:, [
        0, 2, 3, 16, 17, 18, 19, 25, 33, 35, 36, 37, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 55, 58, 60, 61, 65, 66, 67, 68, 69, 70, 74, 75, 76]]

    # 訓練データを正規化
    train_data_df = normalization(train_data_df_raw)
    train_data = train_data_df.to_numpy()

    print('train data')
    print(train_data.shape)

    # ターゲットデータ（期待値）
    train_targets_df = df_train['SalePrice']
    train_targets_df = train_targets_df.reset_index().drop(columns='MSSubClass')
    train_targets = train_targets_df.to_numpy().reshape(-1)
    print('train target')
    print(train_targets.shape)

    # 試験データ
    df_test = load_file('./datasets/test.csv')
    # # 暫定的に数値のデータだけ使用する
    test_data_raw = df_test.iloc[:, [
        0, 2, 3, 16, 17, 18, 19, 25, 33, 35, 36, 37, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 53, 55, 58, 60, 61, 65, 66, 67, 68, 69, 70, 74, 75, 76]]
    # テストデータを正規化
    test_data_df = normalization_train_data = normalization(
        test_data_raw)
    test_data = test_data_df.to_numpy()

    test_targets_df = load_file('./datasets/sample_submission.csv')
    # test_targets_df = test_targets_df['SalePrice']
    test_targets_df = test_targets_df.drop(columns='Id')
    test_targets = test_targets_df.to_numpy().reshape(-1)

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
except Exception as e:
    print(vars(e))
