#-*- coding:utf-8 -*-

# 이 라이브러리는 부산대 한국어 맞춤법/문법 검사기를 파이썬에서 사용하기 위한 것입니다.
# 라이선스 등에 대해서는 부산대학교 인공지능연구실에 문의해 주세요.

import requests
import urllib
import cgi
import HTMLParser

import re

correction_table_re = re.compile(
    u"""<DIV id='correctionTable' style='display:none; width:300px; height:200px;'>(.+)<DIV id='correctionTable2' style='display:none; width:300px; height:200px;'>(.+)</body>""",
    re.MULTILINE|re.DOTALL
    )
underline_re = re.compile(
    u"""<div id='bufUnderline' style='display:none; width:300px; height:200px;'>(.+)</div>""",
    re.MULTILINE|re.DOTALL
    )

error_word_re = re.compile(
    u"""<font id='ul_(\\d+)' color='([#a-zA-Z0-9]+)' class='ul' onclick="fShowHelp\('\d+'\)" >([^<]+)</font>""",
    re.MULTILINE
    )

replace_re = re.compile(
    u"""<TD id='tdErrorWord_\\d+' class='tdErrWord' style='color:[#a-zA-Z0-9]+;' >(.+?)</TD>.+?<TD id='tdReplaceWord_\\d+' class='tdReplace' >(.+?)</TD>.+?<TD id='tdHelp_\\d+?' class='tdETNor'>(.+?)</TD>""",
    re.MULTILINE|re.DOTALL
    )

splitter_re = re.compile("(\s+)", re.MULTILINE)

def unescape(origin):
    return origin.replace("&amplt", "<").replace("&ampgt", ">").replace("&amp", "&")

def speller(origin, encoding="utf-8"):
    """입력된 문자열에서 맞춤법이 잘못된 부분을 찾아서 반환한다.

    :param origin: 맞춤법을 검사할 문자열
    :type origin: :class:`basestring`
    :param encoding: (origin이 string일 경우) origin의 인코딩
    :type encoding: :class:`basestring`

    :returns: 다음 내용으로 구성된 dict의 리스트
            level: 에러 레벨 (unicode)
            start_pos: 시작 위치 (int)
            length: 길이 (int)
            error_word: 입력 내용 (unicode)
            replace_word: 수정 내용 (list of unicode)
            help: 도움말 (unicode)
            
    :rtype: :class:`list`
    """
    if not isinstance(origin, basestring):
        raise TypeError("origin must be a string, not " + repr(origin))
    if not isinstance(encoding, basestring):
        raise TypeError("encoding must be a string, not " + repr(encoding))

    if isinstance(origin, str): # 문자 인코딩을 utf-8로 맞춘다.
        origin = origin.decode(encoding)
    origin = origin.encode("utf-8")

    splitted_origin = splitter_re.split(origin)

    error_words = []

    start_pos = 0 # 텍스트의 누적 시작위치. LCS등을 사용하지 않아도 되도록 트리키하게 접근.

    for idx in xrange(0, len(splitted_origin), 600):
        target = str.join("", splitted_origin[idx:idx+600])

        params = {'text1': target}
        r = requests.post("http://speller.cs.pusan.ac.kr/PnuSpellerISAPI_201209/lib/PnuSpellerISAPI_201209.dll?Check"
                        , data=params)

        raw_result = r.content.decode('utf-8')
        raw_correction_datas = correction_table_re.search(raw_result)
        correction_datas = raw_correction_datas.groups() # correction_datas[0] : 1차 교정 테이블.
                                                         # correction_datas[1] : 2차 교정 테이블
                                                         # 2차 교정 테이블은 아직 지원하지 않는다.

        raw_source = underline_re.search(correction_datas[0])
        if raw_source is None:
            start_pos += len(unescape(target))
            continue

        source = raw_source.groups()
        replaces = replace_re.findall(correction_datas[0])
        replaces_idx = 0
        raw_end_pos = 0

        for m in error_word_re.finditer(source[0]):
            start_pos -= len(source[0][raw_end_pos:m.start()]) - len(unescape(source[0][raw_end_pos:m.start()]))
            error_words.append({'level': m.group(2),
                                'start_pos': start_pos + (m.start() - raw_end_pos),
                                'length': len(m.group(3)),
                                'error_word': m.group(3),
                                'replace_word': replaces[replaces_idx][1].split('<br/>')[:-1],
                                'help': replaces[replaces_idx][2]})

            start_pos += (m.start() - raw_end_pos) + len(m.group(3))
            raw_end_pos = m.end()
            replaces_idx += 1

        start_pos -= len(source[0][raw_end_pos:]) - len(unescape(unescape(source[0][raw_end_pos:])))
        start_pos += len(source[0]) - raw_end_pos

    return error_words
