#!/bin/zsh

function showbindkey() {
    km=test
    v=$(bindkey -N $km && bindkey -M $km -s $1 "" && bindkey -M $km)
    printf "\"%s\" = %s\n" $1 ${v::-3}
}

if (( $# <= 2 )); then
    printf "function showbindkey defined, use: showbindkey <keycode>\n"
    return 0
fi

if (( $# < 3 )); then
    printf "Usage bindkey_test.zsh <width=2|4|8> <start> <end>\n"
    return 1
fi

width=$1
start=$2
end=$3

declare -A prefix
prefix=([2]=x [4]=u [8]=U)

format="\\\\${prefix[$width]}%0${width}X"
printf "width=%d,start=%08X,end=%08X,format=%s\n" $width $start $end $format

for (( i = $start; i <= $end; i++ )); do
    showbindkey $(printf $format $i)
done
