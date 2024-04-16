#!/bin/zsh

keymap=test
output=/tmp/bindkey_test.txt

: > $output
for (( i = 0x00; i <= 0xff; i++ )); do
    printf -v hex "%02X" $i
    code=$(bindkey -N $keymap && bindkey -M $keymap -s "\x$hex" "" && bindkey -M $keymap)
    printf "0x%s = %s\n" $hex $code >> $output
done
eval $EDITOR $output