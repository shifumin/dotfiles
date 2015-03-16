set nocompatible " vi互換の動作を無効にする
set backspace=indent,eol,start "バックスペースでインデントや改行を削除できるようにする

"#####表示設定#####
syntax on " コードの色分けする
colorscheme desert " カラースキーマの指定
" 行番号の色
highlight LineNr ctermfg=darkyellow
set background=dark " 暗い背景色に合わせた配色にする
set title " 編集中のファイル名を表示する
set number " 行数を表示する
set ruler " カーソルが何行目の何列目に置かれているかを表示する
set showcmd " 入力中のコマンドを表示する
set showmatch " 括弧入力時に対応する括弧を表示する
set cmdheight=2 " コマンドラインに使われる画面上の行数
set laststatus=2 " エディタウィンドウの末尾から2行目にステータスラインを常時表示させる


set tabstop=2 " インデントをスペース4つ分に設定する
set shiftwidth=2 " 自動インデントの幅
set autoindent " 改行時に前の行のインデントを継続する
set smartindent " 改行時に入力された行の末尾に合わせて次の行のインデントを増減する
set expandtab " タブ入力を複数の空白入力に置き換える
set smarttab " 行頭の余白内でTabを打ち込むと"shiftwidth"の数だけインデントする
set whichwrap=b,s,h,l,<,>,[,] " カーソルを行頭、行末で止まらないようにする


"#####検索設定#####
set ignorecase " 大文字/小文字の区別なく検索する
set smartcase " 検索文字列に大文字が含まれている場合は区別して検索する
set wrapscan " 検索時に最後まで行ったら最初に戻る
set incsearch " インクリメンタルサーチ
set hlsearch " 検索マッチテキストをハイライト

"--------------------
"" 基本的な設定
"--------------------

" バックアップファイルのディレクトリを指定する
set backupdir=$HOME/vimbackup

set noswapfile " スワップファイルを使用しない
set wildmenu " コマンドラインモードで<Tab>キーによるファイル名保管を有効にする
