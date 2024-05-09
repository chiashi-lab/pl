# PL連続NDフィルターの制御
![overview](docs/fig1.png)

data/

--手動で測定したデータを保存するディレクトリ

notebook/

--analysis.ipynb dataディレクトリに保存されたデータを解析するノートブック

src/

--config.py パラメータ設定

--ophircom.py パワーメータのクラス定義

--thorlab.py 連続NDフィルターが設置されたステージのクラス定義

--superchrome.py レーザー波長可変フィルターsuperchromeのクラス定義

--ihr320.py 分光器IHR320のクラス定義

--symphony.py 検出器symphonyのクラス定義

--func.py ノートブックで算出された関数の定義

--main.py 全体の自動制御のテストコード

## ステージコントロール

[https://pylablib.readthedocs.io/en/latest/devices/Thorlabs_kinesis.html](https://pylablib.readthedocs.io/en/latest/devices/Thorlabs_kinesis.html)

pipでインストール可能なpylablibを使用して制御

## パワメ数値取得
[OphirManual](docs/OphirLMMeasurement_COM_Object_0.pdf)

ophirのstarlabにpythonのデモがある

## superchrome
[superchromeSDK](docs/SuperChromeSDK.pdf)

dllファイルから制御しようとしたときに4108エラーが発生。（金井がdelphiのサンプルコードを理解できていないのが原因。多分何とかなるハズ）

どうしようもないのでdll同梱の制御GUIをpywinautoによって直接操作している
