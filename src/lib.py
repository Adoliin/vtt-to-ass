import re
import os
import pysubs2

# --ReGex patterns--
re_subLineVtt = re.compile(
    r"\d\d:\d\d:\d\d\.\d\d\d --> \d\d:\d\d:\d\d\.\d\d\d"
)
re_subLineAss = re.compile(
    r"\d,\d:\d\d:\d\d\.\d\d,\d:\d\d:\d\d\.\d\d"
)

def vttToAss(subPathVtt):
    pys2_subs = pysubs2.load(subPathVtt)
    linesVtt = readSubFile(subPathVtt)

    tmp_subPathAss = os.path.join(os.getcwd(), 'tmp_sub.vtt')
    pys2_subs.save(tmp_subPathAss)
    tmp_linesAss = readSubFile(tmp_subPathAss)
    os.remove(tmp_subPathAss)

    slVtt = getSubLines(linesVtt, re_subLineVtt)
    slAss = getSubLines(tmp_linesAss, re_subLineAss)
    subLines = mergeSubLines(slVtt, slAss)
    fixed_linesAss = fixMarginTop(subLines, linesVtt, tmp_linesAss)
    fixed_linesAss = fixWeirdChars(subLines, linesVtt, fixed_linesAss)
    return ''.join(fixed_linesAss)

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
