""""""""""""""""""""""""""""""
" Search:
""""""""""""""""""""""""""""""
" Ignore the case of normal letters.
set ignorecase
" If the search pattern contains upper case characters, override ignorecase option.
set smartcase
" Enable incremental search.
set incsearch
" Don't highlight search result.
set nohlsearch
" Searches wrap around the end of the file.
set wrapscan
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Edit:
""""""""""""""""""""""""""""""
" Smart insert tab setting.
set smarttab
" Exchange tab to spaces.
set expandtab
" Substitute <Tab> with blanks.
" set tabstop=8
" Spaces instead <Tab>.
" set softtabstop=4
" Autoindent width.
set shiftwidth=4
" Round indent by shiftwidth.
set shiftround

" Enable smart indent.
set autoindent smartindent

" Disable modeline.
set modelines=0
set nomodeline

" Use clipboard register.

set clipboard& clipboard+=unnamed
if (!has('nvim') || $DISPLAY != '') && has('clipboard')
  if has('unnamedplus')
     set clipboard& clipboard+=unnamedplus
  else
     set clipboard& clipboard+=unnamed
  endif
endif

" Enable backspace delete indent and newline.
set backspace=indent,eol,start

" Highlight <>.
set matchpairs+=<:>

" Display another buffer when current buffer isn't saved.
set hidden

" Search home directory path on cd.
" But can't complete.
"  set cdpath+=~
""""""""""""""""""""""""""""""


" Increase history amount.
set history=1000

set number " 行番号を表示
set cursorline " カーソルラインをハイライト

" 長い行の折り返し表示
set wrap
set display=lastline

" 補完メニューの高さ
set pumheight=10

set whichwrap=b,s,h,l,<,>,[,],~ " カーソルの左右移動で行末から次の行の行頭への移動が可能になる

" 対応する括弧へのジャンプ
set showmatch
set matchtime=1

" バックスペースキーの有効化
set backspace=indent,eol,start

" Vimの「%」を拡張する
source $VIMRUNTIME/macros/matchit.vim


""""""""""""""""""""""""""""""
" Filetype
""""""""""""""""""""""""""""""
autocmd BufRead,BufNewFile *.md set filetype=markdown
autocmd BufRead,BufNewFile *.yml set filetype=yaml
autocmd BufRead,BufNewFile *.html set filetype=html
autocmd BufRead,BufNewFile *.haml set filetype=haml
autocmd BufRead,BufNewFile *.slim set filetype=slim
autocmd BufRead,BufNewFile *.sass set filetype=sass
autocmd BufRead,BufNewFile *.scss set filetype=scss.css
autocmd BufRead,BufNewFile *.js set filetype=javascript
autocmd BufRead,BufNewFile *.json set filetype=json
autocmd BufRead,BufNewFile *.coffee set filetype=coffee
autocmd BufRead,BufNewFile *.rb set filetype=ruby
autocmd BufRead,BufNewFile *.rabl  set filetype=ruby
autocmd BufRead,BufNewFile *.rake set filetype=ruby
autocmd BufRead,BufNewFile .pryrc set filetype=ruby
autocmd BufRead,BufNewFile Gemfile set filetype=ruby
autocmd BufRead,BufNewFile Dockerfile.* set filetype=dockerfile
autocmd FileType javascript setlocal sw=4 sts=4 ts=4 et
autocmd FileType coffee setlocal sw=2 sts=2 ts=2 et
autocmd FileType php setlocal sw=4 sts=4 ts=4 et
autocmd FileType ruby setlocal sw=2 sts=2 ts=2 et

" ?も一続きの単語として認識
autocmd FileType ruby setlocal iskeyword+=?
autocmd FileType css setlocal iskeyword+=-
""""""""""""""""""""""""""""""

" 以下整理する
""""""""""""""""""""""""""""""

" 表示関係

set list                " 不可視文字の可視化
set wrap                " 長いテキストの折り返し
set textwidth=0         " 自動的に改行が入るのを無効化
set colorcolumn=80      " その代わり80文字目にラインを入れる

" デフォルト不可視文字は美しくないのでUnicodeで綺麗に
set listchars=tab:»-,trail:-,extends:»,precedes:«,nbsp:%,eol:↲

" 編集関係

set shiftround          " '<'や'>'でインデントする際に'shiftwidth'の倍数に丸める
set infercase           " 補完時に大文字小文字を区別しない
set virtualedit=all     " カーソルを文字が存在しない部分でも動けるようにする
set hidden              " バッファを閉じる代わりに隠す（Undo履歴を残すため）
set switchbuf=useopen   " 新しく開く代わりにすでに開いてあるバッファを開く
set matchtime=3         " 対応括弧のハイライト表示を3秒にする

" 対応括弧に'<'と'>'のペアを追加
set matchpairs& matchpairs+=<:>

" クリップボードをデフォルトのレジスタとして指定。後にYankRingを使うので
" 'unnamedplus'が存在しているかどうかで設定を分ける必要がある
" if has('unnamedplus')
"     " set clipboard& clipboard+=unnamedplus " 2013-07-03 14:30 unnamed 追加
"     set clipboard& clipboard+=unnamedplus,unnamed
" else
"     " set clipboard& clipboard+=unnamed,autoselect 2013-06-24 10:00 autoselect 削除
"     set clipboard& clipboard+=unnamed
" endif

" Swapファイル？Backupファイル？前時代的すぎ
" なので全て無効化する
set nowritebackup
set nobackup
set noswapfile

"
" http://yuroyoro.hatenablog.com/entry/20120211/1328930819
"
" カレントウィンドウにのみ罫線を引く
augroup cch
  autocmd! cch
  autocmd WinLeave * set nocursorline
  autocmd WinEnter,BufRead * set cursorline
augroup END

hi clear CursorLine
hi CursorLine gui=underline
highlight CursorLine ctermbg=black guibg=black

" 保存時に行末の空白を除去する
autocmd BufWritePre * :%s/\s\+$//ge
" 保存時にtabをスペースに変換する
autocmd BufWritePre * :%s/\t/  /ge


""""""""""""""""""""""""""""""
" 脱初心者を目指すVimmerにオススメしたいVimプラグインや.vimrcの設定 - Qiita
" http://qiita.com/jnchito/items/5141b3b01bced9f7f48f
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" 各種オプションの設定
""""""""""""""""""""""""""""""
" タグファイルの指定(でもタグジャンプは使ったことがない)
set tags=~/.tags
" スワップファイルは使わない(ときどき面倒な警告が出るだけで役に立ったことがない)
set noswapfile
" コマンドラインに使われる画面上の行数
"set cmdheight=2
" ウインドウのタイトルバーにファイルのパス情報等を表示する
set title
" コマンドラインモードで<Tab>キーによるファイル名補完を有効にする
set wildmenu
" バックアップディレクトリの指定(でもバックアップは使ってない)
set backupdir=$HOME/.vimbackup
" バッファで開いているファイルのディレクトリでエクスクローラを開始する(でもエクスプローラって使ってない)
set browsedir=buffer
" 暗い背景色に合わせた配色にする
set background=dark
" タブ入力を複数の空白入力に置き換える
set expandtab
" 保存されていないファイルがあるときでも別のファイルを開けるようにする
set hidden
" 不可視文字を表示する
set list
" タブと行の続きを可視化する
set listchars=tab:>\ ,extends:<
" 改行時に前の行のインデントを継続する
set autoindent
" 改行時に入力された行の末尾に合わせて次の行のインデントを増減する
set smartindent
" タブ文字の表示幅
set tabstop=2
" Vimが挿入するインデントの幅
set shiftwidth=2
" 行頭の余白内で Tab を打ち込むと、'shiftwidth' の数だけインデントする
set smarttab
" 構文毎に文字色を変化させる
syntax on
" カラースキーマの指定
"colorscheme desert
" 行番号の色
highlight LineNr ctermfg=darkyellow
""""""""""""""""""""""""""""""

" http://inari.hatenablog.com/entry/2014/05/05/231307
""""""""""""""""""""""""""""""
" 全角スペースの表示
""""""""""""""""""""""""""""""
function! ZenkakuSpace()
    highlight ZenkakuSpace cterm=underline ctermfg=lightblue guibg=darkgray
endfunction

if has('syntax')
    augroup ZenkakuSpace
        autocmd!
        autocmd ColorScheme * call ZenkakuSpace()
        autocmd VimEnter,WinEnter,BufRead * let w:m1=matchadd('ZenkakuSpace', '　')
    augroup END
    call ZenkakuSpace()
endif
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" 最後のカーソル位置を復元する
""""""""""""""""""""""""""""""
if has("autocmd")
    autocmd BufReadPost *
    \ if line("'\"") > 0 && line ("'\"") <= line("$") |
    \   exe "normal! g'\"" |
    \ endif
endif
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Basic
""""""""""""""""""""""""""""""
" 想定される改行コードの指定する
set fileformats=unix,dos,mac

" 行番号のハイライト設定
hi CursorLineNr term=bold   cterm=NONE ctermfg=6 ctermbg=NONE

" http://vimwiki.net/?%27viminfo%27
" set viminfo='50,\"1000,:0,n~/.vim/viminfo

" ビープ音を全て無効にする
set visualbell t_vb=
set noerrorbells
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" 文字列検索
""""""""""""""""""""""""""""""
set incsearch " インクリメンタルサーチ. １文字入力毎に検索を行う
set ignorecase " 検索パターンに大文字小文字を区別しない
set smartcase " 検索パターンに大文字を含んでいたら大文字小文字を区別する
set hlsearch " 検索結果をハイライト


""""""""""""""""""""""""""""""
" カーソル
""""""""""""""""""""""""""""""
set whichwrap=b,s,h,l,<,>,[,],~ " カーソルの左右移動で行末から次の行の行頭への移動が可能になる
set number " 行番号を表示
set cursorline " カーソルラインをハイライト


"" highlight設定後に書くこと
" Colorscheme Solarized
" let g:solarized_termcolors=256
syntax enable
set background=dark
colorscheme solarized
