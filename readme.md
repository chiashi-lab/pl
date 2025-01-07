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
12. マッピング測定の場合はステージを動かして5~11を繰り返す
13. シャッターとレーザ前ミラーを閉じて終了

## ディレクトリ構成

```
.
├── data...notebookで使うデータを保存するフォルダ
├── docs
│   └── readme用の画像等
├── notebook
│   ├── analyse.ipynb...パワーメータの結果からステージにおけるパワーを推定する式を導出するためのノートブック
│   └── ple.ipynb...PLEマップのデータを解析，2次元ピークフィッティングを行うためのノートブック
├── src
│   ├── main.py...メインスクリプト．計測の中心となる部分の関数を記述している
│   ├── config.py...各デバイスの設定を記述している
│   ├── easylaser_window.py...励起光照射君のGUI．このスクリプトを実行するとGUIが立ち上がる
│   ├── easypl_window.py...PLEマップ測定君のGUI．このスクリプトを実行するとGUIが立ち上がる
│   ├── movingpl_window.py...PLEマップのマッピング測定君のGUI．このスクリプトを実行するとGUIが立ち上がる
│   ├── detectpl_window.py...PLスペクトルのマッピング測定のGUI．このスクリプトを実行するとGUIが立ち上がる
│   ├── func.py...main関数等で使う数式を記述している
│   ├── logger.py...ログを記録するためのクラス定義
│   └──driver
│       ├── brimrose.py...brimrose社製AOTFの制御のためのクラス定義
│       ├── fianium.py...fianium社製LVTFであるsuperchromeの制御のためのクラス定義
│       ├── horiba.py...horiba jovan yvon社製の分光器iHR320とCCD検出器symphonyの制御のためのクラス定義
│       ├── ophir.py...ophir社製のパワーメーターの制御のためのクラス定義
│       ├── prior.py...prior社製のステージコントローラーの制御のためのクラス定義
│       ├── sigmakoki.py...sigmakoki社製のシャッターコントローラーの制御のためのクラス定義
│       └── thorlabs.py...thorlabs社製のNDフィルター用ステージコントローラーとレーザー前のミラーの制御のためのクラス定義
├── .gitignore...gitで無視するファイルを指定するファイル
├── PLEマップのマッピング測定.bat...PLEマップのマッピング測定君を起動するためのバッチファイル
├── PLEマップ測定君.bat...PLEマップ測定君を起動するためのバッチファイル
├── install.bat...必要なライブラリをインストールするためのバッチファイル
├── README.md...このファイル
├── requirements.txt...必要なライブラリを示したファイル
├── update.bat...必要なライブラリをアップデートするためのバッチファイル
└── 励起光照射君.bat...励起光照射君を起動するためのバッチファイル


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