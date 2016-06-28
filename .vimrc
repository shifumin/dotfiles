" Encoding
set encoding=utf-8
scriptencoding utf-8

""""""""""""""""""""""""""""""
" 脱初心者を目指すVimmerにオススメしたいVimプラグインや.vimrcの設定 - Qiita
" http://qiita.com/jnchito/items/5141b3b01bced9f7f48f
" dotfiles/.vimrc · JunichiIto/dotfiles
" https://github.com/JunichiIto/dotfiles/blob/master/.vimrc
""""""""""""""""""""""""""""""

" 挙動を vi 互換ではなく、Vim のデフォルト設定にする
set nocompatible
" 一旦ファイルタイプ関連を無効化する
filetype off

" source .vimrc.neobundle
if filereadable(expand('~/.vimrc.neobundle'))
  source ~/.vimrc.neobundle
endif

" 想定される改行コードの指定する
set fileformats=unix,dos,mac

" Colorscheme Solarized
syntax enable
set background=dark
colorscheme solarized

" O で空行を挿入得する
nnoremap O :<C-u>call append(expand('.'), '')<Cr>j


" -------------------------------
" http://lambdalisue.hatenablog.com/entry/2013/06/23/071344
" -------------------------------

" 表示関係

set list                " 不可視文字の可視化
set number              " 行番号の表示
set wrap                " 長いテキストの折り返し
set textwidth=0         " 自動的に改行が入るのを無効化
" set colorcolumn=80      " その代わり80文字目にラインを入れる

" 前時代的スクリーンベルを無効化
set t_vb=
set novisualbell

" デフォルト不可視文字は美しくないのでUnicodeで綺麗に
set listchars=tab:»-,trail:-,extends:»,precedes:«,nbsp:%,eol:↲


" 検索関係

set ignorecase          " 大文字小文字を区別しない
set smartcase           " 検索文字に大文字がある場合は大文字小文字を区別
set incsearch           " インクリメンタルサーチ
set hlsearch            " 検索マッチテキストをハイライト

" バックスラッシュやクエスチョンを状況に合わせ自動的にエスケープ
cnoremap <expr> / getcmdtype() == '/' ? '\/' : '/'
cnoremap <expr> ? getcmdtype() == '?' ? '\?' : '?'


" 編集関係

set shiftround          " '<'や'>'でインデントする際に'shiftwidth'の倍数に丸める
set infercase           " 補完時に大文字小文字を区別しない
set virtualedit=all     " カーソルを文字が存在しない部分でも動けるようにする
set hidden              " バッファを閉じる代わりに隠す（Undo履歴を残すため）
set switchbuf=useopen   " 新しく開く代わりにすでに開いてあるバッファを開く
set showmatch           " 対応する括弧などをハイライト表示する
set matchtime=3         " 対応括弧のハイライト表示を3秒にする

" 対応括弧に'<'と'>'のペアを追加
set matchpairs& matchpairs+=<:>

" バックスペースでなんでも消せるようにする
set backspace=indent,eol,start

" クリップボードをデフォルトのレジスタとして指定。後にYankRingを使うので
" 'unnamedplus'が存在しているかどうかで設定を分ける必要がある
if has('unnamedplus')
    " set clipboard& clipboard+=unnamedplus " 2013-07-03 14:30 unnamed 追加
    set clipboard& clipboard+=unnamedplus,unnamed
else
    " set clipboard& clipboard+=unnamed,autoselect 2013-06-24 10:00 autoselect 削除
    set clipboard& clipboard+=unnamed
endif

" Swapファイル？Backupファイル？前時代的すぎ
" なので全て無効化する
set nowritebackup
set nobackup
set noswapfile


"
" http://yuroyoro.hatenablog.com/entry/20120211/1328930819
"

  " カーソル行をハイライト
  set cursorline
  " カレントウィンドウにのみ罫線を引く
  augroup cch
    autocmd! cch
    autocmd WinLeave * set nocursorline
    autocmd WinEnter,BufRead * set cursorline
  augroup END

hi clear CursorLine
hi CursorLine gui=underline
highlight CursorLine ctermbg=black guibg=black

"Escの2回押しでハイライト消去
nmap <ESC><ESC> :nohlsearch<CR><ESC>

" Ctrl-iでヘルプ
nnoremap <C-i>  :<C-u>help<Space>
" カーソル下のキーワードをヘルプでひく
nnoremap <C-i><C-i> :<C-u>help<Space><C-r><C-w><Enter>

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
" カーソルが何行目の何列目に置かれているかを表示する
set ruler
" コマンドラインに使われる画面上の行数
"set cmdheight=2
" エディタウィンドウの末尾から2行目にステータスラインを常時表示させる
set laststatus=2
" ステータス行に表示させる情報の指定(どこからかコピペしたので細かい意味はわかっていない)
set statusline=%<%f\ %m%r%h%w%{'['.(&fenc!=''?&fenc:&enc).']['.&ff.']'}%=%l,%c%V%8P
" ステータス行に現在のgitブランチを表示する
set statusline+=%{fugitive#statusline()}
" ウインドウのタイトルバーにファイルのパス情報等を表示する
set title
" コマンドラインモードで<Tab>キーによるファイル名補完を有効にする
set wildmenu
" 入力中のコマンドを表示する
set showcmd
" バックアップディレクトリの指定(でもバックアップは使ってない)
set backupdir=$HOME/.vimbackup
" バッファで開いているファイルのディレクトリでエクスクローラを開始する(でもエクスプローラって使ってない)
set browsedir=buffer
" 小文字のみで検索したときに大文字小文字を無視する
set smartcase
" 検索結果をハイライト表示する
set hlsearch
" 暗い背景色に合わせた配色にする
set background=dark
" タブ入力を複数の空白入力に置き換える
set expandtab
" 検索ワードの最初の文字を入力した時点で検索を開始する
set incsearch
" 保存されていないファイルがあるときでも別のファイルを開けるようにする
set hidden
" 不可視文字を表示する
set list
" タブと行の続きを可視化する
set listchars=tab:>\ ,extends:<
" 行番号を表示する
set number
" 対応する括弧やブレースを表示する
set showmatch
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
" カーソルを行頭、行末で止まらないようにする
set whichwrap=b,s,h,l,<,>,[,]
" 構文毎に文字色を変化させる
syntax on
" カラースキーマの指定
"colorscheme desert
" 行番号の色
highlight LineNr ctermfg=darkyellow
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Vimの便利な画面分割＆タブページと、それを更に便利にする方法 - Qiita
" http://qiita.com/tekkoc/items/98adcadfa4bdc8b5a6ca
""""""""""""""""""""""""""""""
nnoremap s <Nop>
nnoremap sj <C-w>j
nnoremap sk <C-w>k
nnoremap sl <C-w>l
nnoremap sh <C-w>h
nnoremap sJ <C-w>J
nnoremap sK <C-w>K
nnoremap sL <C-w>L
nnoremap sH <C-w>H
nnoremap sn gt
nnoremap sp gT
nnoremap sr <C-w>r
nnoremap s= <C-w>=
nnoremap sw <C-w>w
nnoremap so <C-w>_<C-w>|
nnoremap sO <C-w>=
nnoremap sN :<C-u>bn<CR>
nnoremap sP :<C-u>bp<CR>
nnoremap st :<C-u>tabnew<CR>
nnoremap sT :<C-u>Unite tab<CR>
nnoremap ss :<C-u>sp<CR>
nnoremap sv :<C-u>vs<CR>
nnoremap sq :<C-u>q<CR>
nnoremap sQ :<C-u>bd<CR>
nnoremap sb :<C-u>Unite buffer_tab -buffer-name=file<CR>
nnoremap sB :<C-u>Unite buffer -buffer-name=file<CR>
call submode#enter_with('bufmove', 'n', '', 's>', '<C-w>>')
call submode#enter_with('bufmove', 'n', '', 's<', '<C-w><')
call submode#enter_with('bufmove', 'n', '', 's+', '<C-w>+')
call submode#enter_with('bufmove', 'n', '', 's-', '<C-w>-')
call submode#map('bufmove', 'n', '', '>', '<C-w>>')
call submode#map('bufmove', 'n', '', '<', '<C-w><')
call submode#map('bufmove', 'n', '', '+', '<C-w>+')
call submode#map('bufmove', 'n', '', '-', '<C-w>-')
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

" https://sites.google.com/site/fudist/Home/vim-nihongo-ban/-vimrc-sample
""""""""""""""""""""""""""""""
" 挿入モード時、ステータスラインの色を変更
""""""""""""""""""""""""""""""
let g:hi_insert = 'highlight StatusLine guifg=darkblue guibg=darkyellow gui=none ctermfg=blue ctermbg=yellow cterm=none'

if has('syntax')
  augroup InsertHook
    autocmd!
    autocmd InsertEnter * call s:StatusLine('Enter')
    autocmd InsertLeave * call s:StatusLine('Leave')
  augroup END
endif

let s:slhlcmd = ''
function! s:StatusLine(mode)
  if a:mode == 'Enter'
    silent! let s:slhlcmd = 'highlight ' . s:GetHighlight('StatusLine')
    silent exec g:hi_insert
  else
    highlight clear StatusLine
    silent exec s:slhlcmd
  endif
endfunction

function! s:GetHighlight(hi)
  redir => hl
  exec 'highlight '.a:hi
  redir END
  let hl = substitute(hl, '[\r\n]', '', 'g')
  let hl = substitute(hl, 'xxx', '', '')
  return hl
endfunction
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

set viminfo='50,\"3000,:0,n~/.viminfo

""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" key mapping
""""""""""""""""""""""""""""""
" [Vim] インサートモード時の便利キーマップ - Qiita
" http://qiita.com/y_uuki/items/14389dbaaa43d25f3254
""""""""""""""""""""""""""""""
" insertモードから抜ける
inoremap <silent> jj <ESC>
inoremap <silent> <C-j> j
inoremap <silent> kk <ESC>
inoremap <silent> <C-k> k

" 行頭・行末移動方向をキーの相対位置にあわせる
" nnoremap 0 $
" nnoremap 1 0

" 挿入モードでのカーソル移動
inoremap <C-j> <Down>
inoremap <C-k> <Up>
inoremap <C-h> <Left>
inoremap <C-l> <Right>

" カーソル前の文字削除
inoremap <silent> <C-h> <C-g>u<C-h>
" カーソル後の文字削除
inoremap <silent> <C-d> <Del>
" カーソルから行頭まで削除
inoremap <silent> <C-d>e <Esc>lc^
" カーソルから行末まで削除
inoremap <silent> <C-d>0 <Esc>lc$
" カーソルから行頭までヤンク
inoremap <silent> <C-y>e <Esc>ly0<Insert>
" カーソルから行末までヤンク
inoremap <silent> <C-y>0 <Esc>ly$<Insert>

" 引用符, 括弧の設定
" inoremap { {}<Left>
" inoremap [ []<Left>
" inoremap ( ()<Left>
" inoremap " ""<Left>
" inoremap ' ''<Left>
" inoremap <> <><Left>

" Ctags用タグスタックを戻るキーバインド
nnoremap <c-[> :pop<CR>


""""""""""""""""""""""""""""""
" vimgrep
""""""""""""""""""""""""""""""
" vimgrepとQuickfix知らないVimmerはちょっとこっち来い - Qiita
" http://qiita.com/yuku_t/items/0c1aff03949cb1b8fe6b
""""""""""""""""""""""""""""""
nnoremap [q :cprevious<CR>   " 前へ
nnoremap ]q :cnext<CR>       " 次へ
nnoremap [Q :<C-u>cfirst<CR> " 最初へ
nnoremap ]Q :<C-u>clast<CR>  " 最後へ
" grep検索の実行後にQuickFix Listを表示する
autocmd QuickFixCmdPost *grep* cwindow

""""""""""""""""""""""""""""""
" PHP settings
""""""""""""""""""""""""""""""
" VimでPHP開発環境を作成 - Qiita
" http://qiita.com/NanohaAsOnKai/items/0188fb3b60e8a79656a0
""""""""""""""""""""""""""""""

" $VIMRUNTIME/syntax/php.vim
let g:php_baselib       = 1
let g:php_htmlInStrings = 1
let g:php_noShortTags   = 1
let g:php_sql_query     = 1

" <? をハイライト除外にする
let g:php_noShortTags         = 1
" カッコが閉じていない場合にハイライト
let g:php_parent_error_close  = 1

" $VIMRUNTIME/syntax/sql.vim
let g:sql_type_default = 'mysql'

" 辞書ファイルの読込
autocmd FileType php,ctp :set dictionary=~/.vim/dict/php.dict

""""""""""""""""""""""""""""""
" 実践Vim
""""""""""""""""""""""""""""""

" 記録するコマンド履歴検索履歴の数
set history=200

" 履歴からコマンドを呼び戻すときにカーソルキーを使わない
cnoremap <C-p> <Up>
cnoremap <C-n> <Down>

""
" Original
""
" ヤンクした内容が消えないようにする
noremap PP "0p
noremap x "_x

" 閉じ括弧補完
inoremap {<Enter> {}<Left><CR><ESC><S-o>
inoremap [<Enter> []<Left><CR><ESC><S-o>
inoremap (<Enter> ()<Left><CR><ESC><S-o>


" filetypeの自動検出
filetype on
