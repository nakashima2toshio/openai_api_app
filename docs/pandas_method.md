#### Pandas重要メソッド一覧
| カテゴリ                   | 操作名／メソッド                | 概要（簡易版）                                            | 利用例                                                            |
|----------------------------|---------------------------------|-----------------------------------------------------------|-------------------------------------------------------------------|
| データ確認                 | `df.head(n)`                    | 先頭n行を表示（デフォルト5）                               | `df.head(10)`                                                     |
| データ確認                 | `df.tail(n)`                    | 末尾n行を表示（デフォルト5）                               | `df.tail(10)`                                                     |
| データ確認                 | `df.info()`                     | 列ごとの型や欠損値の有無などを表示                         | `df.info()`                                                       |
| データ確認                 | `df.describe()`                 | 基本統計量（平均・中央値など）を表示                       | `df.describe()`                                                   |
| データ確認                 | `df.shape`                      | 行数と列数をタプルで取得                                   | `df.shape`                                                        |
| データ確認                 | `df.columns`                    | 列名を一覧表示                                            | `df.columns`                                                      |
| データ確認                 | `df.index`                      | インデックスを一覧表示                                    | `df.index`                                                        |
| データ確認                 | `df.dtypes`                     | 各列のデータ型を取得                                      | `df.dtypes`                                                       |
| データ確認                 | `df.isnull()`                   | 欠損値の有無を確認                                        | `df.isnull().sum()`                                               |
| データ確認                 | `df.nunique()`                  | 各列のユニークな値の数を確認                              | `df.nunique()`                                                    |
| データ確認                 | `df['column'].value_counts()`   | 指定列の値ごとの出現頻度を取得                            | `df['col'].value_counts()`                                        |
| データ確認(追加)           | `df.memory_usage()`             | 各列のメモリ使用量を確認                                  | `df.memory_usage(deep=True)`                                      |
| データ選択                 | `df.loc[]`                      | ラベル名で行・列を選択                                    | `df.loc[0:5, ['col1','col2']]`                                   |
| データ選択                 | `df.iloc[]`                     | インデックス番号で行・列を選択                            | `df.iloc[0:5, 0:2]`                                              |
| データ選択                 | `df.at[]`                       | 特定のラベル位置の値を取得（高速）                        | `df.at[0, 'col1']`                                               |
| データ選択                 | `df.iat[]`                      | 特定の位置の値を取得（高速）                              | `df.iat[0, 1]`                                                    |
| データ選択                 | `df.query("条件")`              | 条件式でデータを抽出                                      | `df.query('col1 > 50')`                                           |
| データ選択                 | `df.sample(n)`                  | ランダムにn行抽出                                         | `df.sample(5)`                                                    |
| データの加工               | `df.sort_values(by=)`           | 指定列でソート                                            | `df.sort_values(by='col1', ascending=False)`                      |
| データの加工               | `df.sort_index()`               | インデックスでソート                                      | `df.sort_index(ascending=False)`                                  |
| データの加工               | `df.rename(columns=)`           | 列名を変更                                                | `df.rename(columns={'old':'new'})`                                |
| データの加工               | `df.drop()`                     | 行や列を削除                                              | `df.drop(['col1'], axis=1)`                                       |
| データの加工               | `df.fillna(value)`              | 欠損値を埋める                                            | `df.fillna(0)`                                                    |
| データの加工               | `df.dropna()`                   | 欠損値のある行・列を削除                                  | `df.dropna()`                                                     |
| データの加工               | `df.astype()`                   | データ型を変更                                            | `df['col1'].astype(float)`                                        |
| データの加工               | `df.replace()`                  | 値の置換                                                  | `df.replace({'old_value': 'new_value'})`                          |
| データの加工               | `df.apply()`                    | 各列または各行に関数を適用                                | `df.apply(np.sum, axis=0)`                                        |
| データの加工(Series用)     | `df['col'].map()`              | Series各要素に関数を適用（列単位）                        | `df['col'].map(lambda x: x*2)`                                    |
| データの加工            | `df.applymap()`                 | DataFrame全体の要素ごとに関数を適用                       | `df.applymap(str)`                                                |
| データの加工             | `df.drop_duplicates()`          | 重複行を削除                                              | `df.drop_duplicates(subset=['col1', 'col2'], keep='first')`       |
| データの追加・結合         | `pd.concat()`                   | DataFrameを縦・横方向に連結                               | `pd.concat([df1, df2], axis=0)`                                   |
| データの追加・結合         | `df.merge()`                    | キーを使ってデータを結合（JOIN操作）                       | `df1.merge(df2, on='key')`                                        |
| データの追加・結合         | `df.join()`                     | インデックスを使ってDataFrameを結合                       | `df1.join(df2)`                                                   |
| データの追加・結合         | `df.assign()`                   | 新しい列を追加                                            | `df.assign(new_col=df['col1']*2)`                                 |
| データの変形(追加)         | `df.pivot()`                    | 行(index), 列(columns), 値(values)を指定してピボット       | `df.pivot(index='col1', columns='col2', values='val')`            |
| データの変形(追加)         | `df.melt()`                     | 列を行方向にまとめる(逆ピボット)                           | `df.melt(id_vars=['id'], var_name='variable', value_name='value')`|
| データ集約・グループ化     | `df.groupby()`                  | グループ化                                                | `df.groupby('col1').mean()`                                       |
| データ集約・グループ化     | `df.pivot_table()`              | ピボット集計テーブルを作成                                | `df.pivot_table(values='val', index='col1', columns='col2')`      |
| データ集約・グループ化     | `df.aggregate()` (`agg()`)      | 集約関数を適用（mean, sum等）                              | `df.agg(['mean','sum'])`                                          |
| データ集約・グループ化   | `pd.crosstab()`                 | クロス集計表を作成（関数）                                | `pd.crosstab(df['col1'], df['col2'])`                             |
| データの入出力             | `pd.read_csv()`                 | CSVを読み込む                                             | `pd.read_csv('file.csv')`                                         |
| データの入出力             | `df.to_csv()`                   | CSVとして保存                                             | `df.to_csv('output.csv', index=False)`                            |
| データの入出力             | `pd.read_excel()`               | Excelを読み込む                                           | `pd.read_excel('file.xlsx')`                                      |
| データの入出力             | `df.to_excel()`                 | Excelファイルとして保存                                   | `df.to_excel('output.xlsx', index=False)`                         |
| データの入出力             | `pd.read_json()`                | JSONを読み込む                                            | `pd.read_json('file.json')`                                       |
| データの入出力             | `df.to_json()`                  | JSONとして出力                                            | `df.to_json('output.json')`                                       |



