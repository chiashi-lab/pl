# PLの制御
![overview](docs/fig1.png)

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

obj/ --メーカー提供のライブラリを格納するディレクトリ

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