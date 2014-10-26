set nocompatible
set backspace=indent,eol,start

"#####表示設定#####
set title "編集中のファイル名を表示する
syntax on "コードの色分けする
set number "行数を表示する
set tabstop=4 "インデントをスペース4つ分に設定する
set shiftwidth=4 "自動インデントの幅
set smartindent "オートインデント
set showmatch "括弧入力時に対応する括弧を表示する

"#####検索設定#####
set ignorecase "大文字/小文字の区別なく検索する
set smartcase "検索文字列に大文字が含まれている場合は区別して検索する
set wrapscan "検索時に最後まで行ったら最初に戻る
set incsearch "インクリメンタルサーチ
set hlsearch "検索マッチテキストをハイライト

"--------------------
"" 基本的な設定
"--------------------
"新しい行のインデントを現在行と同じにする
set autoindent 

"バックアップファイルのディレクトリを指定する
set backupdir=$HOME/vimbackup
