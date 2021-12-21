import re
import os
import sys, getopt
import pysubs2

usage_message = \
'''\
Usage:
    vttToAss --input SOURCE --output DEST
    or
    vttToAss -i SOURCE -o DEST\
'''

# --GLOBAL VARIABLES--
SUB_PATH_VTT = ''
TMP_SUB_PATH_ASS = ''
SUB_PATH_ASS = ''

# --ReGex patterns--
re_subLineVtt = re.compile(
    r"\d\d:\d\d:\d\d\.\d\d\d --> \d\d:\d\d:\d\d\.\d\d\d"
)
re_subLineAss = re.compile(
    r"\d,\d:\d\d:\d\d\.\d\d,\d:\d\d:\d\d\.\d\d"
)

def main():
    getOpts()
    pys2_subs = pysubs2.load(SUB_PATH_VTT)
    pys2_subs.save(TMP_SUB_PATH_ASS)
    linesVtt = readSubFile(SUB_PATH_VTT)
    tmp_linesAss = readSubFile(TMP_SUB_PATH_ASS)
    slVtt = getSubLines(linesVtt, re_subLineVtt)
    slAss = getSubLines(tmp_linesAss, re_subLineAss)
    subLines = mergeSubLines(slVtt, slAss)
    fixed_linesAss = fixMarginTop(subLines, linesVtt, tmp_linesAss)
    fixed_linesAss = fixWeirdChars(subLines, linesVtt, fixed_linesAss)
    writeSubFile(SUB_PATH_ASS, ''.join(fixed_linesAss))
    os.remove(TMP_SUB_PATH_ASS)
    print(f'Sub converted: {SUB_PATH_ASS}')

def getOpts():
    global SUB_PATH_VTT, TMP_SUB_PATH_ASS, SUB_PATH_ASS
    try:
        opts, _ = getopt.getopt(
            sys.argv[1:],
            ":i:o:h", ["input=", "output=", "help"]
        )

    except getopt.GetoptError as err:
        print(err)
        print(usage_message)
        sys.exit(1)

    if not opts:
        print('No arguments were provided!')
        print(usage_message)
        sys.exit(1)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(usage_message)
            sys.exit()
        elif opt in ("-i", "--input"):
            try:
                SUB_PATH_VTT = os.path.abspath(arg)
            except:
                print(f'{arg} is not a valid input path')
                print(usage_message)
                sys.exit(1)
        elif opt in ("-o", "--output"):
            try:
                SUB_PATH_ASS = os.path.abspath(arg)
            except:
                print(f'{arg} is not a valid output path')
                print(usage_message)
                sys.exit(1)
            else:
                l = os.path.split(os.path.abspath(arg))
                TMP_SUB_PATH_ASS = os.path.join(
                    l[0], f"tmp_{l[1]}"
                )
        else:
            assert False, "unhandled option"

def mergeSubLines(slVtt, slAss):
    if len(slVtt) == len(slAss):
        subLines = []
        for i in range(len(slVtt)):
            subLines.append({
                'vtt': slVtt[i],
                'ass': slAss[i],
            })
    return subLines

def fixMarginTop(subLines, linesVtt, linesAss):
    max_margin_top_ass = 285
    for sl in subLines:
        lPercent = re.search(r'line:\d+%', linesVtt[sl['vtt']])
        if lPercent:
            percentMatch = re.search(r'\d+', lPercent.group())
            margin_top_vttPercent = int(percentMatch.group())
            margin_top_ass = int(round(
                max_margin_top_ass * (margin_top_vttPercent / 100)
            ))
            tmp = re.sub(r'0,0,0,,', fr'0,0,{margin_top_ass},,{{\\a6}}', linesAss[sl['ass']])
            linesAss[sl['ass']] = tmp
    return linesAss

def fixWeirdChars(subLines, linesVtt, linesAss):
    # replace "&amp;" with "&"
    for sl in subLines:
        tmp = re.sub('&amp;', "&", linesAss[sl['ass']])
        if tmp != linesAss[sl['ass']]:
            linesAss[sl['ass']] = tmp
    return linesAss

def fixSubBeforeSub(subLines, linesVtt, linesAss):
    # fixes a when a sub is not finished and the other
    # come right before the first one finishes,
    # causing one to shift up by a little.
    # (this issue is caused by ffmpeg when converting)
    pass

def getSubLines(lines, reComp):
    indexList = []
    for i, line in enumerate(lines):
        if reComp.findall(line):
            indexList.append(i)
    return indexList

def readSubFile(subPath):
    with open(subPath) as subFile:
        lines = subFile.readlines()
    return lines

def writeSubFile(subPath, lines):
    with open(subPath, 'w') as subFile:
        subFile.write(lines)

if __name__ == '__main__':
    main()
