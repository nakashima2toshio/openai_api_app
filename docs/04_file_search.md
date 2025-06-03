#### File Search
#### 機能概要
File Searchは、あらかじめベクターストア（vector store）にファイルをアップロードし、
自動的にパース・チャンク・埋め込み（embedding）して格納したうえで、
ユーザーのクエリに対してセマンティック検索とキーワード検索を組み合わせて関連情報を返す機能です。

| No. | 機能                             | プログラム名                              |
| --- | -------------------------------- | ----------------------------------------- |
| 1   | ベーシック検索（Basic）          | file_search_basic.py                      |
| 2   | 検索結果数の制限（Limit）        | file_search_limit.py                      |
| 3   | 検索結果情報の展開（Include）    | file_search_include_results.py            |
| 4   | メタデータフィルタ（Filter）     | file_search_with_filters.py               |

##### 事前準備（Fileをvector storeへ）
・ファイルのアップロード
・自動で、パース、チャンク、埋め込み・embedding(Vector化)
・vector storeに登録する。


