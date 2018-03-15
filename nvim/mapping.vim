" terminal modeでnormal modeに戻る
tnoremap <silent> <ESC> <C-\><C-n>

" 誤動作防止
map q: :q

"Escキーの2回押しでハイライトを消去
nnoremap <ESC><ESC> :nohlsearch<CR>

" insertモードから抜ける
inoremap <silent> jj <ESC>

" 履歴からコマンドを呼び戻すときにカーソルキーを使わない
cnoremap <C-p> <Up>
cnoremap <C-n> <Down>

"" 削除置換ヤンク
" ヤンクした内容が消えないようにする
nnoremap PP "0p
nnoremap x "_x
nnoremap dd "_dd

" 行頭,行末までの色々
nnoremap dh d0
nnoremap dl d$
nnoremap ch c0
nnoremap cl c$
nnoremap yh y0
nnoremap yl y$
nnoremap Y y$

"" 移動系
" 高速移動
noremap J 20j
noremap K 20k
noremap L 10l
noremap H 10h

"" 入力系
" バックスラッシュやクエスチョンを状況に合わせ自動的にエスケープ
cnoremap <expr> / getcmdtype() == '/' ? '\/' : '/'
cnoremap <expr> ? getcmdtype() == '?' ? '\?' : '?'

" O で空行を挿入する
nnoremap O :<C-u>call append(expand('.'), '')<Cr>j
" I でスペースを挿入する
nnoremap I a <Esc>

"" タブウィンドウ
" Ctags用タグスタックを戻るキーバインド
nnoremap <c-[> :pop<CR>
" [tag vertical] 縦にウィンドウを分割してジャンプ
nnoremap tv :vsplit<CR> :exe("tjump ".expand('<cword>'))<CR>
nnoremap ts :split<CR> :exe("tjump ".expand('<cword>'))<CR>
" 新しいタブを開いてジャンプ
nnoremap <F3> :<C-u>tab stj <C-R>=expand('<cword>')<CR><CR>
nnoremap tw :<C-u>tab stj <C-R>=expand('<cword>')<CR><CR>

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
" nnoremap sT :<C-u>Unite tab<CR>
nnoremap ss :<C-u>sp<CR>
nnoremap sv :<C-u>vs<CR>
nnoremap sq :<C-u>q<CR>
nnoremap sQ :<C-u>bd<CR>
" nnoremap sb :<C-u>Unite buffer_tab -buffer-name=file<CR>
" nnoremap sB :<C-u>Unite buffer -buffer-name=file<CR>
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
" Leader key settings
""""""""""""""""""""""""""""""
" LeaderをSpaceキーにする
let mapleader = "\<Space>"
nnoremap <Leader>w :w<CR>
nnoremap <Leader>q :q<CR>
nnoremap <Leader>v V
nnoremap <Leader>i <C-i>
nnoremap <Leader>o <C-o>
nnoremap <Leader>g :<C-u>Ggrep<Space>
nnoremap <Leader>k :<C-u>call<Space>ref#K('normal')<CR>
nnoremap <Leader>n :<C-u>NERDTreeToggle<CR>
nnoremap <Leader>f :<C-u>NERDTreeFind<CR>
nnoremap <Leader>s :<C-u>QuickRun<CR>
nnoremap <Leader>t :<C-u>Tlist<CR>
nnoremap <Leader>co :copen<CR>
nnoremap <Leader>cc :cclose<CR>
nnoremap <Leader>cn :cnewer<CR>
nnoremap <Leader>cp :colder<CR>
" nnoremap <Leader>z :<C-u>sp ~/project/trash.txt<CR>
nnoremap <Leader>sw :w !sudo tee % > /dev/null<CR>

" Ruby
nnoremap <Leader>bp obinding.pry<Esc>:<C-u>w<CR>

" Python
nnoremap <Leader>l :call Flake8()<CR>

" rails.vim
nnoremap <Leader>em :<C-u>Emodel<CR>
nnoremap <Leader>ev :<C-u>Eview<CR>
nnoremap <Leader>ec :<C-u>Econtroller<CR>

"" denite.vim
" nnoremap <Leader>u :<C-u>Denite file_mru buffer<CR>
nnoremap <silent> <Leader><Leader>u :<C-u>Denite file_mru buffer -highlight-mode-insert=Search<CR>
" カレントディレクトリ以下の再帰検索
nnoremap <silent> <Leader><Leader>c :<C-u>Denite file_rec<CR>
" カーソル以下の単語をgrep
nnoremap <silent> <Leader><Leader>w :<C-u>DeniteCursorWord grep -buffer-name=search line<CR><C-R><C-W><CR>

" 普通にgrep
" nnoremap <silent> ,g :<C-u>Denite -buffer-name=search -mode=normal grep<CR>
" search
" nnoremap <silent> ,/ :<C-u>Denite -buffer-name=search -auto-resize line<CR>

" resume previous buffer
nnoremap <silent> ,r :<C-u>Denite -buffer-name=search -resume -mode=normal<CR>
" resumeした検索結果の次の行の結果へ飛ぶ
nnoremap <silent> ,n :<C-u>Denite -resume -buffer-name=search -select=+1 -immediately<CR>
" resumeした検索結果の前の行の結果へ飛ぶ
nnoremap <silent> ,p :<C-u>Denite -resume -buffer-name=search -select=-1 -immediately<CR>

" search dotfiles
nnoremap <silent> <Leader><Leader>d :<C-u>Denite -buffer-name=search file_rec:~/dotfiles/<CR>

nnoremap <silent> <Leader><Leader>r :<C-u>Denite -buffer-name=register register neoyank<CR>
xnoremap <silent> <Leader><Leader>r :<C-u>Denite -default-action=replace -buffer-name=register register neoyank<CR>
nnoremap <silent> <Leader><Leader>/ :<C-u>Denite -buffer-name=search -auto-highlight line<CR>
nnoremap <silent> <Leader><Leader>* :<C-u>DeniteCursorWord -buffer-name=search -auto-highlight -mode=normal line<CR>
nnoremap <silent> <Leader><Leader>s :<C-u>Denite file_point file_old
        \ -sorters=sorter_rank
        \ `finddir('.git', ';') != '' ? 'file_rec/git' : 'file_rec'`<CR>

nnoremap <silent> <Leader><Leader>gr :<C-u>Denite -buffer-name=search -no-empty -mode=normal grep<CR>
nnoremap <silent> <Leader><Leader>gs :<C-u>Denite gitstatus<CR>
nnoremap <silent> <Leader><Leader>: :<C-u>Denite command command_history<CR>

"" denite-rails
nnoremap [rails] <Nop>
nmap     <Leader>r [rails]
nnoremap [rails]r :Denite<Space>rails:
nnoremap <silent> [rails]r :<C-u>Denite<Space>rails:dwim<Return>
nnoremap <silent> [rails]m :<C-u>Denite<Space>rails:model<Return>
nnoremap <silent> [rails]c :<C-u>Denite<Space>rails:controller<Return>
nnoremap <silent> [rails]v :<C-u>Denite<Space>rails:view<Return>
nnoremap <silent> [rails]h :<C-u>Denite<Space>rails:helper<Return>
nnoremap <silent> [rails]r :<C-u>Denite<Space>rails:test<Return>
nnoremap <silent> [rails]s :<C-u>Denite<Space>rails:spec<Return>
""""""""""""""""""""""""""""""
