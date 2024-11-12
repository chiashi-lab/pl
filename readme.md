# PLの制御
python == 3.11.9
![overview](docs/fig1.png)

1. レーザ前ミラーとシャッターの起動。二つで光路を遮断
2. チューナブルフィルタの起動。（チューナブルフィルタ起動時に白色レーザーがまるまる射出されて危険なので必ず光路を閉じる）
3. レーザ前ミラーを開く
4. パワーメーターとCCD検出器の起動
5. 励起光中心波長と励起光波長幅を設定.
6. パワーメーターの値が安定するまで少し待ってからPID制御でパワーを調整
7. シャッターを開き、レーザーをサンプルに照射
8. CCD検出器を露光しデータを取得
9. シャッターを閉じる
10. CCD検出器からおくられてきたデータをリネーム。指定されたフォルダに"励起光中心波長.txt"として保存
11. 励起光最短中心波長から励起光最長中心波長まで励起光中心波長間隔ごとにずらしながら5~10を繰り返す
12. シャッターとレーザ前ミラーを閉じて終了

## ディレクトリ構成

```
PL.bat --GUI起動用バッチファイル

data/ --手動で測定したデータを保存するディレクトリ

notebook/
|--analysis.ipynb dataディレクトリに保存されたデータを解析するノートブック

src/
|--config.py パラメータ設定
|--func.py ノートブックで算出された関数の設定
|--ophircom.py パワーメータのクラス定義
|--thorlab.py 連続NDフィルターが設置されたステージおよびターミネータへのミラーが設置されたフリップマウント制御のクラス定義
|--superchrome.py レーザー波長可変フィルターsuperchrome制御のクラス定義
|--ihr320.py 分光器IHR320制御のクラス定義
|--symphony.py 検出器symphony制御のクラス定義
|--main.py 全体の自動制御コード
|--window.py GUIの処理を行うコード


docs/ --メーカー提供のドキュメントを格納するディレクトリ

```

## ステージコントロール

[https://pylablib.readthedocs.io/en/latest/devices/Thorlabs_kinesis.html](https://pylablib.readthedocs.io/en/latest/devices/Thorlabs_kinesis.html)


## パワメ数値取得
[OphirManual](docs/OphirLMMeasurement_COM_Object_0.pdf)


## superchrome
[superchromeSDK](docs/SuperChromeSDK.pdf)

dllファイルから制御しようとしたときに4108エラーが発生。（金井がdelphiのサンプルコードを理解できていないのが原因。多分何とかなるハズ）

どうしようもないのでdll同梱の制御GUIをpywinautoによって直接操作している

## 分光器 ihR320

こちらもpywinautoで直接MonoExampleを操作している

## 検出器 symphony

こちらもpywinautoで直接CCDExampleを操作している