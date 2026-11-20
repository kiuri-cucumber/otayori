# otayori

学校や役所から来る資料を読み取り、家族のカレンダーに予定と締め切りを入れる道具です。

## いまできること

- 文字が埋め込まれた PDF とテキストを読む。
- 日付つきの予定と締め切り、持ち物を拾う(令和の日付、全角の数字、年のない日付に対応)。
- SQLite に残す。同じ資料は二重に登録しない。
- iPhone のカレンダーで購読できる `.ics` を出す。

## 使い方

```bash
python3.11 -m app add tests/fixtures/sample_otayori.txt
```

```bash
python3.11 -m app feed > otayori.ics
```

## 検査

```bash
python3.11 -m unittest discover -s tests -t .
```

## 決まり

- 家族の実物の資料は `data/` か `tests/fixtures/private/` に置く。どちらもリポジトリに入らない。
- リポジトリに入れる見本は、作りものだけにする。

## これから

1. スキャンの PDF と写真の OCR。
2. モデルを使った読み取り(決まった書き方から外れたお便り)。
3. 人が確かめる画面。
4. 出産日から逆算する役所の届け出。
5. 音声での入力。
