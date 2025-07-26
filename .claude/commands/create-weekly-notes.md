# create-weekly-notes

## 概要
今週と来週のウィークリーノートとデイリーノートを作成します。

## 使用方法
```
/create-weekly-notes
```

## 動作
1. **重要**: 環境情報の「Today's date」から今日の日付を必ず確認し、それを基準に今週と来週の週番号を計算
2. 各週の月曜日から日曜日までの日付を計算
3. テンプレートを読み込み:
   - デイリーノート: `005_Template/テンプレ_デイリーノート.md`
   - ウィークリーノート: `005_Template/テンプレ_ウィークリーノート.md`
4. デイリーノートを作成（各週7日分）:
   - ファイル名: `010_Daily/YYYY-MM-DD.md`
   - Templater記法を適切な値に置換
   - updated_atを作成時刻で設定
5. ウィークリーノートを作成（2週分）:
   - ファイル名: `011_Weekly/YYYY-W##.md`
   - 各週のデイリーノートを埋め込み
   - updated_atを作成時刻で設定
6. 既存ファイルはスキップして報告

## 注意事項
- Writeツールで直接作成（UTF-8エンコーディング確保）
- touchコマンドは使用しない（文字化け防止）
- Templater記法の置換:
  - `<% tp.date.now("YYYY-MM-DD", -1, tp.file.title, "YYYY-MM-DD") %>` → 前日の日付
  - `<% tp.date.now("YYYY-MM-DD", 1, tp.file.title, "YYYY-MM-DD") %>` → 翌日の日付
  - `<% tp.date.now("YYYY-[W]WW", 0, tp.file.title, "YYYY-MM-DD") %>` → 週番号