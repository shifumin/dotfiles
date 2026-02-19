# Notionへの保存 技術仕様

SKILL.mdから参照されるNotion-flavored Markdown変換ルール。
完全な仕様は MCP resource `notion://docs/enhanced-markdown-spec` を参照。

## 目次

1. テーブル変換
2. 引用ブロック
3. Toggle
4. カラー指定
5. コードブロック
6. 空行の扱い
7. 使用を避けるべき書式
8. よくある変換ミス

## 1. テーブル変換

標準Markdownのパイプテーブルは使用不可。XML形式で記述する。

**変換前**（標準Markdown）:

```markdown
| 列1 | 列2 |
|-----|-----|
| A   | B   |
```

**変換後**（Notion-flavored Markdown）:

```xml
<table header-row="true">
	<tr>
		<td>列1</td>
		<td>列2</td>
	</tr>
	<tr>
		<td>A</td>
		<td>B</td>
	</tr>
</table>
```

主な属性:

| 属性 | 説明 | デフォルト |
|------|------|-----------|
| `header-row` | 最初の行をヘッダーにする | false |
| `header-column` | 最初の列をヘッダーにする | false |
| `fit-page-width` | ページ幅に合わせる | false |

セルにカラーを指定: `<td color="red_bg">テキスト</td>`
行にカラーを指定: `<tr color="blue_bg">`

セル内の書式はNotion Markdown記法を使用（`**bold**`等）。HTMLタグ（`<strong>`等）は不可。

## 2. 引用ブロック

単一行:

```markdown
> テキスト
```

複数行（1つのブロックにまとめる場合）:

```markdown
> 行1<br>行2<br>行3
```

**注意**: 複数の `>` 行は別々の引用ブロックになる（標準Markdownと異なる）。

## 3. Toggle

```html
<details>
<summary>トグルタイトル</summary>
	子要素（タブでインデント必須）
</details>
```

Toggle heading:

```markdown
## テキスト {toggle="true"}
	子要素（タブでインデント必須）
```

**重要**: 子要素をインデントしないとトグル内に含まれない。

## 4. カラー指定

テキストカラー: `gray`, `brown`, `orange`, `yellow`, `green`, `blue`, `purple`, `pink`, `red`
背景カラー: `gray_bg`, `brown_bg`, `orange_bg`, `yellow_bg`, `green_bg`, `blue_bg`, `purple_bg`, `pink_bg`, `red_bg`

ブロック全体に色を付ける:

```markdown
テキスト {color="blue"}
```

インラインで色を付ける:

```html
<span color="red">赤いテキスト</span>
```

## 5. コードブロック

````markdown
```ruby
def hello
  puts "Hello, World!"
end
```
````

**重要**: コードブロック内では特殊文字のエスケープ不要。`[`, `]`, `\` 等もそのまま記述する。

## 6. 空行の扱い

- 空行（改行のみ）は自動的に削除される
- 明示的な空行が必要な場合は `<empty-block/>` を使用
- 通常はNotionが適切な間隔を自動設定するため不要

## 7. 使用を避けるべき書式

| 書式 | 理由 |
|------|------|
| callout（`::: callout`） | `mcp__notion__notion-create-pages` でプレーンテキストとして表示される不具合あり |

代替手段:
- 強調したい内容 → `**太字**` + 見出し（`##`, `###`）で対応
- 色付き強調 → `<span color="red">テキスト</span>` で対応

## 8. よくある変換ミス

| ミス | 正しい対処 |
|------|-----------|
| 標準Markdownのパイプテーブルを使用 | `<table>` XML形式に変換 |
| 複数行の引用を `>` 行で分離 | `<br>` で結合して1つの `>` にまとめる |
| コードブロック内で `\[` 等のエスケープ | エスケープ不要、そのまま記述 |
| ページタイトルを content に含める | `properties.title` のみで設定 |
| callout構文を使用 | 太字+見出し or spanカラーで代替 |
| Toggle の子要素をインデントしない | タブでインデント必須 |
