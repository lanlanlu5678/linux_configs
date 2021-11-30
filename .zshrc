# Lines configured by zsh-newuser-install
HISTFILE=~/.histfile
HISTSIZE=1000
SAVEHIST=10000
setopt autocd nomatch
bindkey -v
# End of lines configured by zsh-newuser-install
# The following lines were added by compinstall
zstyle :compinstall filename '/home/lanlanlu/.zshrc'

autoload -Uz compinit
compinit
# End of lines added by compinstall

# Convinient
alias ll='ls -lh'
alias la='ls -alh'
alias pm='pacman'
alias rm='rm -i'
alias rs='rsync -amv --exclude-from=/home/lanlanlu/.rsrule /home/lanlanlu/ /data/configs'
