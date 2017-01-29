""""""""""""""""""""""""""""""
" PHP Plugin
""""""""""""""""""""""""""""""
" The neocomplete source for PHP
" NeoBundle 'violetyk/neocomplete-php.vim'

" Multi-language DBGP debugger client for Vim
" NeoBundle 'joonty/vdebug'

" smarty syntax
" NeoBundle 'vim-scripts/smarty-syntax'

" Use fabpot/PHP-CS-Fixer
" NeoBundleLazy 'stephpy/vim-php-cs-fixer', {'functions': 'PhpCsFixerFixFile'}
""""""""""""""""""""""""""""""
""""""""""""""""""""""""""""""
" PHP Settings
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

""""""""""""""""""""""""""""""
" Vdebug
""""""""""""""""""""""""""""""
let g:vdebug_force_ascii = 1
let g:vdebug_features = {'max_data': 65536, 'max_depth': 16, 'max_children': 1024}
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" neocomplete-php.vim
""""""""""""""""""""""""""""""
let g:neocomplete_php_locale = 'ja'
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" vim-qfstatusline
""""""""""""""""""""""""""""""
function! MyStatuslineSyntax() abort "{{{
    return qfstatusline#Update()
endfunction "}}}

function! MyStatuslinePaste() abort "{{{
    if &paste is# 1
        return '(paste)'
    endif
    return ''
  endfunction "}}}

let g:Qfstatusline#UpdateCmd = function('MyStatuslineSyntax')
set laststatus=2
set cmdheight=1
set statusline=\ %t\ %m\ %r\ %h\ %w\ %q\ %{MyStatuslineSyntax()}%=\ %{MyStatuslinePaste()}\ \|\ %Y\ \|\ %{&fileformat}\ \|\ %{&fileencoding}\
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" vim-quickrun
""""""""""""""""""""""""""""""
nnoremap <Leader>run :<C-u>QuickRun<CR>
" nnoremap <Leader>s :<C-u>QuickRun<CR>
let g:quickrun_config = {
\    '_': {
\        'hook/close_buffer/enable_empty_data': 1,
\        'hook/close_buffer/enable_failure':    1,
\        'outputter':                           'multi:buffer:quickfix',
\        'outputter/buffer/close_on_empty':     1,
\        'outputter/buffer/split':              ':botright',
\        'runner':                              'vimproc',
\        'runner/vimproc/updatetime':           600},
\    'watchdogs_checker/_': {
\        'hook/close_quickfix/enable_exit':        1,
\        'hook/back_window/enable_exit':           0,
\        'hook/back_window/priority_exit':         1,
\        'hook/qfstatusline_update/enable_exit':   1,
\        'hook/qfstatusline_update/priority_exit': 2,
\        'outputter/quickfix/open_cmd':            ''},
\    'watchdogs_checker/php': {
\        'command': 'php',
\        'cmdopt':  '-l -d error_reporting=E_ALL -d display_errors=1 -d display_startup_errors=1 -d log_errors=0 -d xdebug.cli_color=0',
\        'exec':    '%c %o %s:p',
\        'errorformat': '%m\ in\ %f\ on\ line\ %l'},}
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" vim-watchdogs
""""""""""""""""""""""""""""""
let s:hooks = neobundle#get_hooks('vim-watchdogs')
function! s:hooks.on_source(bundle) abort "{{{
    "vim-watchdogs
    let g:watchdogs_check_BufWritePost_enable  = 1
    let g:watchdogs_check_CursorHold_enable    = 1
endfunction "}}}
""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""
" Vim-php-cs-fixer
""""""""""""""""""""""""""""""
nnoremap <Leader>php :<C-u>call<Space>PhpCsFixerFixFile()<CR>
let s:hooks = neobundle#get_hooks('vim-php-cs-fixer')
function! s:hooks.on_source(bundle) abort "{{{
    let g:php_cs_fixer_path = "$HOME/.vim/phpCsFixer/php-cs-fixer" " define the path to the php-cs-fixer.phar
    let g:php_cs_fixer_config                 = 'default'
    let g:php_cs_fixer_dry_run                = 0
    let g:php_cs_fixer_enable_default_mapping = 0
    let g:php_cs_fixer_fixers_list            = 'align_equals,align_double_arrow'
    let g:php_cs_fixer_level                  = 'all'
    let g:php_cs_fixer_php_path               = 'php'
    let g:php_cs_fixer_verbose                = 0
endfunction
""""""""""""""""""""""""""""""

" --------------------------------
" neocomplete.vim for PHP
" 要整理
" --------------------------------
"Note: This option must set it in .vimrc(_vimrc).  NOT IN .gvimrc(_gvimrc)!
" Disable AutoComplPop.
let g:acp_enableAtStartup = 0
" Use neocomplete.
let g:neocomplete#enable_at_startup = 1
" Use smartcase.
let g:neocomplete#enable_smart_case = 1
" Set minimum syntax keyword length.
let g:neocomplete#sources#syntax#min_keyword_length = 3
let g:neocomplete#lock_buffer_name_pattern = '\*ku\*'

" Define dictionary.
let g:neocomplete#sources#dictionary#dictionaries = {
      \ 'default' : '',
      \ 'vimshell' : $HOME.'/.vimshell_hist',
      \ 'scheme' : $HOME.'/.gosh_completions'
      \ }

" Define keyword.
if !exists('g:neocomplete#keyword_patterns')
  let g:neocomplete#keyword_patterns = {}
endif
let g:neocomplete#keyword_patterns['default'] = '\h\w*'

" Plugin key-mappings.
inoremap <expr><C-g>     neocomplete#undo_completion()
inoremap <expr><C-l>     neocomplete#complete_common_string()

" Recommended key-mappings.
" <CR>: close popup and save indent.
inoremap <silent> <CR> <C-r>=<SID>my_cr_function()<CR>
function! s:my_cr_function()
  return neocomplete#close_popup() . "\<CR>"
  " For no inserting <CR> key.
  "return pumvisible() ? neocomplete#close_popup() : "\<CR>"
endfunction
" <TAB>: completion.
inoremap <expr><TAB>  pumvisible() ? "\<C-n>" : "\<TAB>"
" <C-h>, <BS>: close popup and delete backword char.
inoremap <expr><C-h> neocomplete#smart_close_popup()."\<C-h>"
inoremap <expr><BS> neocomplete#smart_close_popup()."\<C-h>"
inoremap <expr><C-y>  neocomplete#close_popup()
inoremap <expr><C-e>  neocomplete#cancel_popup()
" Close popup by <Space>.
"inoremap <expr><Space> pumvisible() ? neocomplete#close_popup() : "\<Space>"

" For cursor moving in insert mode(Not recommended)
"inoremap <expr><Left>  neocomplete#close_popup() . "\<Left>"
"inoremap <expr><Right> neocomplete#close_popup() . "\<Right>"
"inoremap <expr><Up>    neocomplete#close_popup() . "\<Up>"
"inoremap <expr><Down>  neocomplete#close_popup() . "\<Down>"
" Or set this.
"let g:neocomplete#enable_cursor_hold_i = 1
" Or set this.
"let g:neocomplete#enable_insert_char_pre = 1

" AutoComplPop like behavior.
"let g:neocomplete#enable_auto_select = 1

" Shell like behavior(not recommended).
"set completeopt+=longest
"let g:neocomplete#enable_auto_select = 1
"let g:neocomplete#disable_auto_complete = 1
"inoremap <expr><TAB>  pumvisible() ? "\<Down>" : "\<C-x>\<C-u>"

" Enable omni completion.
autocmd FileType css setlocal omnifunc=csscomplete#CompleteCSS
autocmd FileType html,markdown setlocal omnifunc=htmlcomplete#CompleteTags
autocmd FileType javascript setlocal omnifunc=javascriptcomplete#CompleteJS
autocmd FileType python setlocal omnifunc=pythoncomplete#Complete
autocmd FileType xml setlocal omnifunc=xmlcomplete#CompleteTags
"let g:neocomplete#sources#omni#input_patterns.perl = '\h\w*->\h\w*\|\h\w*::'
