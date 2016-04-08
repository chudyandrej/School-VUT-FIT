#!/usr/bin/env bash

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# IPP - cls - doplňkové testy - 2015/2016
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Činnost: 
# - vytvoří výstupy studentovy úlohy v daném interpretu na základě sady testů
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# Popis (README):
#
# Struktura skriptu _stud_tests.sh (v kódování UTF-8):
# Každý test zahrnuje až 4 soubory (vstupní soubor, případný druhý vstupní 
# soubor, výstupní soubor, soubor logující chybové výstupy *.err (zde vynechány)
# a soubor logující návratový kód skriptu *.!!!). 
# Pro spuštění testů je nutné do stejného adresáře zkopírovat i 
# váš skript. V komentářích u jednotlivých testů jsou uvedeny dodatečné 
# informace jako očekávaný návratový kód. 
# Tyto doplňující testy obsahují i několik testů rozšíření (viz konec skriptu).
#
# Proměnné ve skriptu _stud_tests.sh pro konfiguraci testů:
#  INTERPRETER - využívaný interpret 
#  EXTENSION - přípona souboru s vaším skriptem (jméno skriptu je dáno úlohou) 
#  LOCAL_IN_PATH/LOCAL_OUT_PATH - testování různých cest ke vstupním/výstupním
#    souborům
#  
# Další soubory archivu s doplňujícími testy:
# V adresáři ref-out najdete referenční soubory pro výstup (*.out nebo *.xml), 
# referenční soubory s návratovým kódem (*.!!!) a pro ukázku i soubory s 
# logovaným výstupem ze standardního chybového výstupu (*.err). Pokud některé 
# testy nevypisují nic na standardní výstup nebo na standardní chybový výstup, 
# tak může odpovídající soubor v adresáři chybět nebo mít nulovou velikost.
#
# Doporučení a poznámky k testování:
# Tento skript neobsahuje mechanismy pro automatické porovnávání výsledků vašeho 
# skriptu a výsledků referenčních (viz adresář ref-out). Pokud byste rádi 
# využili tohoto skriptu jako základ pro váš testovací rámec, tak doporučujeme 
# tento mechanismus doplnit.
# Dále doporučujeme testovat různé varianty relativních a absolutních cest 
# vstupních a výstupních souborů, k čemuž poslouží proměnné začínající 
# LOCAL_IN_PATH a LOCAL_OUT_PATH (neomezujte se pouze na zde uvedené triviální 
# varianty). 
# Výstupní soubory mohou při spouštění vašeho skriptu již existovat a pokud není 
# u zadání specifikováno jinak, tak se bez milosti přepíší!           
# Výstupní soubory nemusí existovat a pak je třeba je vytvořit!
# Pokud běh skriptu skončí s návratovou hodnotou různou od nuly, tak není 
# vytvoření souboru zadaného parametrem --output nutné, protože jeho obsah 
# stejně nelze považovat za validní.
# V testech se jako pokaždé určitě najdou nějaké chyby nebo nepřesnosti, takže 
# pokud nějakou chybu najdete, tak na ni prosím upozorněte ve fóru příslušné 
# úlohy (konstruktivní kritika bude pozitivně ohodnocena). Vyhrazujeme si také 
# právo testy měnit, opravovat a případně rozšiřovat, na což samozřejmě 
# upozorníme na fóru dané úlohy.
#
# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

TASK=cls
#INTERPRETER="php -d open_basedir=\"\""
#EXTENSION=php
INTERPRETER=python3
EXTENSION=py

# cesty ke vstupním a výstupním souborům
LOCAL_IN_PATH="./" # (simple relative path)
LOCAL_IN_PATH2="" #Alternative 1 (primitive relative path)
LOCAL_IN_PATH3=`pwd`"/" #Alternative 2 (absolute path)
LOCAL_OUT_PATH="./" # (simple relative path)
LOCAL_OUT_PATH2="" #Alternative 1 (primitive relative path)
LOCAL_OUT_PATH3=`pwd`"/" #Alternative 2 (absolute path)
# cesta pro ukládání chybového výstupu studentského skriptu
LOG_PATH="./"


# test01: zakladni strom dedicnosti; Expected output: test01.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test01.in --output=${LOCAL_OUT_PATH}test01.out 2> ${LOG_PATH}test01.err
echo -n $? > test01.!!!

diff test01.\!\!\! ./ref-out/test01.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test01"
fi

java -jar jexamxml.jar test01.out ./ref-out/test01.out delta.xml cls_options >/dev/null

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test01"
fi

echo "test01 complete"

# test02: vypis bazove tridy; Expected output: test02.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test02.in > ${LOCAL_OUT_PATH}test02.out --details=A 2> ${LOG_PATH}test02.err
echo -n $? > test02.!!!

diff test02.\!\!\! ./ref-out/test02.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test02"
fi

java -jar jexamxml.jar test02.out ./ref-out/test02.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test02"
fi

echo "test02 complete"

# test03: vypis dedici tridy; Expected output: test03.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test03.in --output=${LOCAL_OUT_PATH}test03.out --details=D 2> ${LOG_PATH}test03.err
echo -n $? > test03.!!!

diff test03.\!\!\! ./ref-out/test03.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test03"
fi

java -jar jexamxml.jar test03.out ./ref-out/test03.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test03"
fi

echo "test03 complete"


# test04: dedeni ciste virtualni metody => vsechny tridy abstraktni; Expected output: test04.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION < ${LOCAL_IN_PATH3}test04.in > ${LOCAL_OUT_PATH}test04.out 2> ${LOG_PATH}test04.err
echo -n $? > test04.!!!

diff test04.\!\!\! ./ref-out/test04.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test04"
fi

java -jar jexamxml.jar test04.out ./ref-out/test04.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test04"
fi

echo "test04 complete"


# test05: prepsani ciste virtualni metody => dedici tridy nejsou abstraktni; Expected output: test05.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test05.in --output=${LOCAL_OUT_PATH}test05.out 2> ${LOG_PATH}test05.err
echo -n $? > test05.!!!

diff test05.\!\!\! ./ref-out/test05.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test05"
fi

java -jar jexamxml.jar test05.out ./ref-out/test05.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test05"
fi

echo "test05 complete"


# test06: dedici schema diamant => konflikt pri dedeni; Expected output: test06.out; Expected return code: 21
$INTERPRETER $TASK.$EXTENSION --output=${LOCAL_OUT_PATH3}test06.out < ${LOCAL_IN_PATH}test06.in --details=D 2> ${LOG_PATH}test06.err
echo -n $? > test06.!!!

diff test06.\!\!\! ./ref-out/test06.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test06"
fi

echo "test06 complete"


# test07: dedici schema diamant => zabraneni konfliktu prepsanim konf. clenu; Expected output: test07.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --details=D --input=${LOCAL_IN_PATH}test07.in --output=${LOCAL_OUT_PATH2}test07.out 2> ${LOG_PATH}test07.err
echo -n $? > test07.!!!

diff test07.\!\!\! ./ref-out/test07.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test07"
fi

java -jar jexamxml.jar test07.out ./ref-out/test07.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test07"
fi

echo "test07 complete"


# test08: reseni konfliktu pri dedeni kl. slovem using; Expected output: test08.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test08.in --output=${LOCAL_OUT_PATH3}test08.out --details=C 2> ${LOG_PATH}test08.err
echo -n $? > test08.!!!

diff test08.\!\!\! ./ref-out/test08.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test08"
fi

java -jar jexamxml.jar test08.out ./ref-out/test08.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test08"
fi

echo "test08 complete"


# test09: ukazka hlubsiho vypisu lesu dedicnosti; Expected output: test09.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH2}test09.in --output=${LOCAL_OUT_PATH}test09.out 2> ${LOG_PATH}test09.err
echo -n $? > test09.!!!

diff test09.\!\!\! ./ref-out/test09.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test09"
fi

java -jar jexamxml.jar test09.out ./ref-out/test09.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test09"
fi

echo "test09 complete"


# test10: vypsani detailu vsech trid v souboru; Expected output: test10.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --details --input=${LOCAL_IN_PATH3}test10.in --output=${LOCAL_OUT_PATH}test10.out 2> ${LOG_PATH}test10.err
echo -n $? > test10.!!!

diff test10.\!\!\! ./ref-out/test10.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test10"
fi

java -jar jexamxml.jar test10.out ./ref-out/test10.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test10"
fi

echo "test10 complete"


# test11: Vyhledavani pomoci XPath; Expected output: test11.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH}test11.in --output=${LOCAL_OUT_PATH2}test11.out --details --search="/model/class[*/attributes/attribute/@name='var']/@name" 2> ${LOG_PATH}test11.err
echo -n $? > test11.!!!

diff test11.\!\!\! ./ref-out/test11.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test11"
fi

java -jar jexamxml.jar test11.out ./ref-out/test11.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test11"
fi

echo "test11 complete"


# test12: BONUS: vypis konfliktniho clenu ve tride; Expected output: test12.out; Expected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}test12.in --output=${LOCAL_OUT_PATH}test12.out --details=C --conflicts 2> ${LOG_PATH}test12.err
echo -n $? > test12.!!!

diff test12.\!\!\! ./ref-out/test12.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test12"
fi

java -jar jexamxml.jar test12.out ./ref-out/test12.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test12"
fi

echo "test12 complete"


# test13: Nevypsani zdedeneho clenu, ktery byl v dedene tride private a ktery neni pure virtual metodou; Expected output:  test13.out; Exptected return code: 0
$INTERPRETER $TASK.$EXTENSION --input=${LOCAL_IN_PATH3}test13.in --output=${LOCAL_OUT_PATH}test13.out --details=B 2> ${LOG_PATH}test13.err
echo -n $? > test13.!!!

diff test13.\!\!\! ./ref-out/test13.\!\!\! >/dev/null
if [ $? -ne 0 ]; then        
    echo "!!!BAD_ret_code_number_test13"
fi

java -jar jexamxml.jar test13.out ./ref-out/test13.out delta.xml cls_options >/dev/null 

if [ $? -ne 0 ]; then        
    echo "!!!Output and referenced one do not match : test13"
fi

echo "test13 complete"