rm -rf /tmp/*

for file in *; do
    if [ "mkpk" = ${file##*.} ]; then
        ASM_PATH=/tmp/${file%.*}.asm
        OBJ_PATH=/tmp/${file%.*}.o
        EXE_PATH=/tmp/${file%.*}

        python3 ../src/makka_pakka/mkpk_transpile.py ${file} -o ${ASM_PATH}
        nasm -f elf64 -o ${OBJ_PATH} ${ASM_PATH}
        ld ${OBJ_PATH} -o ${EXE_PATH}
    fi
done
