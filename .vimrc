set encoding=utf-8
scriptencoding utf-8

" 一旦ファイルタイプ関連を無効化する
filetype off

" source .vimrc.neobundle
if filereadable(expand('~/.vimrc.neobundle'))
  source ~/.vimrc.neobundle
endif

""""""""""""""""""""""""""""""

" 表示関係

set list                " 不可視文字の可視化
set wrap                " 長いテキストの折り返し
set textwidth=0         " 自動的に改行が入るのを無効化
" set colorcolumn=80      " その代わり80文字目にラインを入れる

" デフォルト不可視文字は美しくないのでUnicodeで綺麗に
set listchars=tab:»-,trail:-,extends:»,precedes:«,nbsp:%,eol:↲

" バックスラッシュやクエスチョンを状況に合わせ自動的にエスケープ
cnoremap <expr> / getcmdtype() == '/' ? '\/' : '/'
cnoremap <expr> ? getcmdtype() == '?' ? '\?' : '?'


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
" カレントウィンドウにのみ罫線を引く
augroup cch
  autocmd! cch
  autocmd WinLeave * set nocursorline
  autocmd WinEnter,BufRead * set cursorline
augroup END

hi clear CursorLine
hi CursorLine gui=underline
highlight CursorLine ctermbg=black guibg=black

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

" original
nnoremap s[ :<C-u>tabm 0<CR>
nnoremap s] :<C-u>tabm<CR>
nnoremap s, :<C-u>tabm -1<CR>
nnoremap s. :<C-u>tabm +1<CR>
nnoremap s1 :<C-u>tabnext1<CR>
nnoremap s2 :<C-u>tabnext2<CR>
nnoremap s3 :<C-u>tabnext3<CR>
nnoremap s4 :<C-u>tabnext4<CR>
nnoremap s5 :<C-u>tabnext5<CR>
nnoremap s6 :<C-u>tabnext6<CR>
nnoremap s7 :<C-u>tabnext7<CR>
nnoremap s8 :<C-u>tabnext8<CR>
nnoremap s9 :<C-u>tabnext9<CR>
nnoremap s0 :<C-u>tabnext10<CR>
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

" Colorscheme Solarized
syntax enable
set background=dark
colorscheme solarized

" 行番号のハイライト設定
hi CursorLineNr term=bold   cterm=NONE ctermfg=6 ctermbg=NONE

" http://vimwiki.net/?%27viminfo%27
set viminfo='50,\"1000,:0,n~/.vim/viminfo

" ビープ音を全て無効にする
set visualbell t_vb=
set noerrorbells
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" key mapping
""""""""""""""""""""""""""""""
" insertモードから抜ける
inoremap <silent> jj <ESC>

" 高速移動
noremap J 20j
noremap K 20k
noremap L 10l
noremap H 10h

" O で空行を挿入する
nnoremap O :<C-u>call append(expand('.'), '')<Cr>j
" I でスペースを挿入する
nnoremap I a <Esc>

" Ctags用タグスタックを戻るキーバインド
nnoremap <c-[> :pop<CR>
" [tag vertical] 縦にウィンドウを分割してジャンプ
nnoremap tv :vsplit<CR> :exe("tjump ".expand('<cword>'))<CR>
nnoremap ts :split<CR> :exe("tjump ".expand('<cword>'))<CR>
" 新しいタブを開いてジャンプ
nnoremap <F3> :<C-u>tab stj <C-R>=expand('<cword>')<CR><CR>
nnoremap tw :<C-u>tab stj <C-R>=expand('<cword>')<CR><CR>
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" 文字列検索
""""""""""""""""""""""""""""""
set incsearch " インクリメンタルサーチ. １文字入力毎に検索を行う
set ignorecase " 検索パターンに大文字小文字を区別しない
set smartcase " 検索パターンに大文字を含んでいたら大文字小文字を区別する
set hlsearch " 検索結果をハイライト

"Escキーの2回押しでハイライトを消去
nnoremap <ESC><ESC> :nohlsearch<CR>
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" カーソル
""""""""""""""""""""""""""""""
set whichwrap=b,s,h,l,<,>,[,],~ " カーソルの左右移動で行末から次の行の行頭への移動が可能になる
set number " 行番号を表示
set cursorline " カーソルラインをハイライト

" 行が折り返し表示されていた場合、行単位ではなく表示行単位でカーソルを移動する
nnoremap j gj
nnoremap k gk
nnoremap <down> gj
nnoremap <up> gk

" バックスペースキーの有効化
set backspace=indent,eol,start

set showmatch " 括弧の対応関係を一瞬表示する
source $VIMRUNTIME/macros/matchit.vim " Vimの「%」を拡張する
""""""""""""""""""""""""""""""

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

""""""""""""""""""""""""""""""
" 実践Vim
""""""""""""""""""""""""""""""
" 記録するコマンド履歴検索履歴の数
set history=200

" 履歴からコマンドを呼び戻すときにカーソルキーを使わない
cnoremap <C-p> <Up>
cnoremap <C-n> <Down>
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Original
""""""""""""""""""""""""""""""
" daw : delete a word カーソル位置の単語を削除
nnoremap da daw
nnoremap ca caw

" 行内での先頭、末尾までの色々
nnoremap dh d0
nnoremap dl d$
nnoremap ch c0
nnoremap cl c$
nnoremap yh y0
nnoremap yl y$

" ヤンクした内容が消えないようにする
nnoremap PP "0p
nnoremap x "_x
nnoremap dd "_dd

" 閉じ括弧補完
inoremap {<Enter> {}<Left><CR><ESC><S-o>
inoremap [<Enter> []<Left><CR><ESC><S-o>
inoremap (<Enter> ()<Left><CR><ESC><S-o>

" 誤動作防止
map q: :q
""""""""""""""""""""""""""""""

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
autocmd FileType javascript setlocal sw=4 sts=4 ts=4 et
autocmd FileType coffee setlocal sw=2 sts=2 ts=2 et
autocmd FileType php setlocal sw=4 sts=4 ts=4 et
autocmd FileType ruby setlocal sw=2 sts=2 ts=2 et
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Leader key settings
""""""""""""""""""""""""""""""
" LeaderをSpaceキーにする
let mapleader = "\<Space>"
nmap <Leader><Leader> V
nnoremap <Leader>w :w<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>i <C-i>
nnoremap <Leader>o <C-o>
nnoremap <Leader>g :<C-u>Ggrep<Space>
nnoremap <Leader>k :<C-u>call<Space>ref#K('normal')<CR>
nnoremap <Leader>n :<C-u>NERDTreeToggle <CR>
nnoremap <Leader>s :<C-u>QuickRun<CR>
nnoremap <Leader>t :<C-u>Tlist<CR>
nnoremap <Leader>co :copen<CR>
nnoremap <Leader>cc :cclose<CR>
nnoremap <Leader>cn :cnewer<CR>
nnoremap <Leader>cp :colder<CR>
nnoremap <Leader>z :<C-u>sp ~/project/trash.txt<CR>
" nnoremap <Leader>b :<C-u>bw! \[quickrun\ output\]<CR>
" nnoremap sw :w !sudo tee % > /dev/null<CR>

" Ruby
nnoremap <Leader>bp obinding.pry<Esc>:<C-u>w<CR>

" Python
nnoremap <Leader>l :call Flake8()<CR>

" unite unite-rails
nnoremap <Leader>u :<C-u>Unite file_mru buffer<CR>
nnoremap <Leader>rm :<C-u>Unite rails/model<CR>
nnoremap <Leader>rc :<C-u>Unite rails/controller<CR>
nnoremap <Leader>rv :<C-u>Unite rails/view<CR>
nnoremap <Leader>rh :<C-u>Unite rails/helper<CR>
nnoremap <Leader>rs :<C-u>Unite rails/stylesheet<CR>
nnoremap <Leader>rj :<C-u>Unite rails/javascript<CR>
nnoremap <Leader>rd :<C-u>Unite rails/db<CR>
nnoremap <Leader>rf :<C-u>Unite rails/config<CR>
nnoremap <Leader>rr :<C-u>Unite rails/route<CR>
nnoremap <Leader>rg :<C-u>Unite rails/gemfile<CR>
nnoremap <Leader>rt :<C-u>Unite rails/spec<CR>
" rails.vim
nnoremap <Leader>em :<C-u>Emodel<CR>
nnoremap <Leader>ev :<C-u>Eview<CR>
nnoremap <Leader>ec :<C-u>Econtroller<CR>
""""""""""""""""""""""""""""""

" filetypeの自動検出
filetype on
