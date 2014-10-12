
set title "編集中のファイル名を表示
syntax on "コードの色分け
set tabstop=4 "画面上でタブ文字が占める幅
set smartindent "オートインデント
set shiftwidth=4 "オートインデント幅
set softtabstop=4 "インデント挿入幅

set ignorecase "大文字/小文字の区別なく検索する
set smartcase "検索文字列に大文字が含まれている場合は区別して検索する
set wrapscan "検索時に最後まで行ったら最初に戻る


"新しい行のインデントを現在行と同じにする
set autoindent

"バックアップファイルのディレクトリを指定する
set backupdir=$HOME/vimbackup

"クリップボードをWindowsと連携する
set clipboard=unnamed

"vi互換をオフする
""スワップファイル用のディレクトリを指定する
set directory=$HOME/vimbackup

"タブの代わりに空白文字を指定する
set expandtab
"
""変更中のファイルでも、保存しないで他のファイルを表示する
set hidden

"インクリメンタルサーチを行う
set incsearch
"
""行番号を表示する
set number

"閉括弧が入力された時、対応する括弧を強調する
set showmatch
"
""新しい行を作った時に高度な自動インデントを行う
set smarttab

"grep検索を表示する
set grepformat=%f:%l:%m,%f:%l%m,%f\ \ %l%m,%f
set grepprg=grep\ -nh
"
""検索結果のハイライトをEsc連打でクリアする
nnoremap <ESC><ESC> :nohlsearch<CR>
 

"改行コードの自動認識
set fileformats=unix,dos,mac

" □とか○の文字があってもカーソル位置がずれないようにする
if exists('&ambiwidth')
        set ambiwidth=double
endif


