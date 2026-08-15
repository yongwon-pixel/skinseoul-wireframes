#!/usr/bin/env python3
r"""R5-A: 노션 미러 파괴 요인 제거 (정본 표기 정리).

근거 = ledger.md F-11·F-12·F-16·F-29·F-30.
노션 컨버터가 표 셀 안의 파이프와 <th>/<td>/<table> 리터럴을 진짜 구분자·태그로
오인해 셀을 쪼개고 열 값을 소실시킨다. 의미는 보존하고 표기만 바꾼다.

안전성(사전 실측):
  - `\|`는 표 행 안에서만 쓰인다(표 밖 0건) → byte-exact QA 어서션에 미노출
  - 위험 태그는 th/td/table 6행뿐 (br·span·b는 노션에서 정상 렌더)

사용: python3 fix_a_notion_safe.py --dry   (미리보기)
      python3 fix_a_notion_safe.py         (적용)
"""
import io, os, re, sys, glob

SPECS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
DRY = '--dry' in sys.argv

def fix_line_pipes(line):
    r"""표 행 안의 `\|` → ` / ` (코드스팬 내부는 ' / ', 산문도 ' / ')."""
    if not line.lstrip().startswith('|') or r'\|' not in line:
        return line, 0
    n = line.count(r'\|')
    # 코드스팬 내부: `a\|b` → `a / b`
    def in_code(m):
        return m.group(0).replace(r'\|', ' / ')
    out = re.sub(r'`[^`\n]*`', in_code, line)
    # 남은(코드스팬 밖) 이스케이프 파이프
    out = out.replace(r'\|', ' / ')
    # 중복 공백 정리 (셀 구분자 | 는 보존)
    out = re.sub(r'  +/', ' /', out)
    out = re.sub(r'/  +', '/ ', out)
    return out, n

def fix_raw_pipes_in_code(line):
    """F-29: 표 행의 인라인 코드 안 '이스케이프 안 된' 생 파이프 → ' / '.
    (마크다운 표 열을 실제로 깨뜨리는 원본 결함)"""
    if not line.lstrip().startswith('|'):
        return line, 0
    cnt = [0]
    def repl(m):
        s = m.group(0)
        if '|' in s and r'\|' not in s:
            cnt[0] += s.count('|')
            return s.replace('|', ' / ')
        return s
    out = re.sub(r'`[^`\n]*`', repl, line)
    return out, cnt[0]

TAG_MAP = {'<th>': 'th', '<td>': 'td', '<table>': 'table',
           '<tr>': 'tr', '<thead>': 'thead', '<tbody>': 'tbody'}

def fix_tags(line):
    """표 행 안 코드스팬의 <th>/<td>/<table> → 꺾쇠 제거 (셀 분할 방지)."""
    if not line.lstrip().startswith('|'):
        return line, 0
    cnt = [0]
    def repl(m):
        s = m.group(0)
        for tag, plain in TAG_MAP.items():
            if tag in s:
                cnt[0] += s.count(tag)
                s = s.replace(tag, plain)
        return s
    out = re.sub(r'`[^`\n]*`', repl, line)
    return out, cnt[0]

def fix_plus_after_backtick(text):
    """F-30: 닫는 백틱 직후의 '+'가 노션에서 '•'로 치환되는 것 방지.
    표 행에서만, `x` + `y` → `x` and `y` 로 의미를 명시."""
    out_lines = []
    n = 0
    for line in text.split('\n'):
        # 비활성: `+`의 의미가 케이스마다 다름(`x` + `y`=and vs `6`+="6 이상").
        # F-30은 개별 검토 대상으로 남기고 기계 치환하지 않는다.
        out_lines.append(line)
    return '\n'.join(out_lines), n

def fix_fence_newline(text):
    """F-16: 닫는 코드펜스 뒤에 붙은 산문을 다음 줄로 분리(노션이 문장을 삼킴)."""
    out, n = [], 0
    for line in text.split('\n'):
        s = line.rstrip()
        if s.startswith('```') and len(s) > 3 and not re.match(r'^```[a-zA-Z0-9]*$', s):
            out.append('```')
            out.append(s[3:].lstrip())
            n += 1
        else:
            out.append(line)
    return '\n'.join(out), n

def main():
    base = os.path.abspath(SPECS_DIR)
    total = {'pipe': 0, 'rawpipe': 0, 'tag': 0, 'plus': 0, 'fence': 0}
    touched = []
    for f in sorted(glob.glob(os.path.join(base, '*.md'))):
        src = io.open(f, encoding='utf-8').read()
        lines = src.split('\n')
        c = {'pipe': 0, 'rawpipe': 0, 'tag': 0}
        for i, line in enumerate(lines):
            line, n = fix_line_pipes(line);       c['pipe'] += n
            line, n = fix_raw_pipes_in_code(line); c['rawpipe'] += n
            line, n = fix_tags(line);              c['tag'] += n
            lines[i] = line
        out = '\n'.join(lines)
        out, np_ = fix_plus_after_backtick(out)
        out, nf = fix_fence_newline(out)
        if out != src:
            name = os.path.basename(f)
            touched.append((name, c['pipe'], c['rawpipe'], c['tag'], np_, nf))
            for k, v in zip(['pipe','rawpipe','tag','plus','fence'],
                            [c['pipe'], c['rawpipe'], c['tag'], np_, nf]):
                total[k] += v
            if not DRY:
                io.open(f, 'w', encoding='utf-8').write(out)
    print(f"{'파일':<26}{'\\|':>5}{'생|':>5}{'태그':>5}{'+':>5}{'펜스':>5}")
    for row in touched:
        print(f"{row[0]:<26}{row[1]:>5}{row[2]:>5}{row[3]:>5}{row[4]:>5}{row[5]:>5}")
    print(f"\n합계: {total}")
    print("DRY RUN — 파일 미변경" if DRY else "적용 완료")

if __name__ == '__main__':
    main()
