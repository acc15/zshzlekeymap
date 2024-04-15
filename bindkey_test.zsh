#!/bin/zsh

keymap=test
output=bindkey_test.txt

: > $output
for (( i = 0x00; i <= 0xff; i++ )); do
    printf -v hex "%02X" $i
    bindkey -N $keymap
    bindkey -M $keymap -s "\x$hex" ""
    code=$(bindkey -M $keymap)
    printf "0x%s = %s\n" $hex $code >> $output
done
bindkey -D $keymap