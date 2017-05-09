import csv
from urllib.request import urlopen
import re

def clean_script(script):
    if len(script) > 75:
        cleaned_script = []
        for line in script:
            character = line[0].lower()
            if 'cut to:' in character or "nb:" in character or "review:" in character \
                or "end review teaser." in character or "prologue:" in character or \
                "buffyworld.com" in character or "fade to black." in character or \
                "closing credits." in character or "written by:" in character or \
                "co-starring:" in character or "special guest star:" in character \
                or "starring:" in character or "disclaimer" in character:
                continue
            if len(character) > 20:
                continue
            character = character.replace('<br>', '')
            character = character.strip().lower()
            dialogue = line[1].replace('<br>', '').replace("&#151;", "-").replace("&nbsp;", " ")
            dialogue = " ".join(dialogue.split())
            cleaned_script.append((character, dialogue))
    else:
        return None
    return script


def hand_parsed_script(count):
    with open('hand_parsed_transcripts/transcript_' + count + '.txt') as transcipt:
        script = []
        for line in transcipt:
            reg = "(?P<character>\w+?):(?P<dialogue>.+)"
            res = re.findall(reg, line)
            if res:
                script.extend(res)
    return script


def parse_script(res, count):
    res = res.replace('&nbsp;', '')
    script = []

    if (count <= 50) or (69 <= count <= 73) or count in [61, 77]:
        res = res.replace('\n\n', '<br>')
        res = res.replace('\n', ' ')
        reg = "(?<=<br>)(?P<character>\w+):(?P<dialogue>.+?)(?=<br>)"
        script = re.findall(reg, res)

    # \n matching
    if count == 75:
        reg = "(?<=\n)(?P<character>.+):[ \t]*(?P<dialogue>.*?)\n"
        script = re.findall(reg, res)

    # <p> matching
    if count == 51 or count == 76:
        x_rep = res.replace('<br>', ' ')
        reg = "(?<=\n<p>)(?P<character>\w+?):(?P<dialogue>.+?)(?=\n<p>)"
        script = re.findall(reg, x_rep, re.DOTALL)

    if count in [59, 62]:
        reg = "\n\n<p>(?P<character>\w+)\s:(?P<dialog>.+)</p>"
        script = re.findall(reg, res)

    if count == 63:
        reg = "(?<=<p>)(?P<character>\w+?)[ \t]*:[ \t]*(?P<dialogue>.+?)(?=</p>)"
        script = re.findall(reg, res)

    if count == 64:
        reg = "\n\n<P>(?P<character>\w+)\s:(?P<dialog>.+)</P>"
        script = re.findall(reg, res)

    # <br> matching
    if count == 52:
        res = res.replace('\n', ' ')
        reg = '(?<=<br>)(?P<character>[A-Z]{2,})(?P<dialogue>.+?)(?=<br>)'
        script = re.findall(reg, res)

    if count in [53, 54, 55, 57, 58, 65, 74]:
        res = res.replace('\n', ' ')
        res = res.replace('<p>', '\n')
        res = res.replace('<BR>', '<br>')
        # reg = '(?<=<br>)(?P<character>\w+):(?P<dialog>.+?)(?=<br>)'
        reg = '(?<=<br>)[ \t]*(?P<character>.+?):(?P<dialog>.+?)(?=<br>)'
        script = re.findall(reg, res)
    
    if 86 <= count <= 122 or count in [79, 80, 81, 82, 84]:
        x_rep = res.replace('\n', '')
        x_rep = x_rep.replace('<br>', '\n')
        x_rep = x_rep.replace('<p>', '\n')
        x_rep = x_rep.replace('<BR>', '\n')
        x_rep = x_rep.replace('<P>', '\n')
        reg = "(?<=\n)(?P<character>.+):[ \t]*(?P<dialogue>.*?)\n"
        script = re.findall(reg, x_rep)

    if count >= 123 and count != 129:
        x_rep = res.replace('\n', '')
        reg = "(?<=<b>)(?P<character>.+?)</b>(?P<dialogue>.+?)(?=</p>)"
        script = re.findall(reg, x_rep)

    if count == 129:
        res = res.replace('\n', '')
        reg = "(?<=<P><B>)(?P<character>\w+?)</B><BR>(?P<dialogue>.+?)(?=</P>)"
        script = re.findall(reg, res)

    if not script:
        return None

    return clean_script(script)


if __name__ == '__main__':
    min_trans = 1
    max_trans = 144

    while min_trans <= max_trans:
        count = str(min_trans)
        while len(count) < 3:
            count = '0' + count
        # 067?
        if min_trans in [46, 56, 60, 66, 67, 68, 78, 83, 85, 116]:
            script = hand_parsed_script(count)
        else:
            url_string = 'http://www.buffyworld.com/buffy/transcripts/' + count + '_tran.html'
            res = urlopen(url_string).read().decode('latin-1')
            script = parse_script(res, min_trans)
        if not script:
            print('error with ', count)
            min_trans += 1
            continue
        print(str(min_trans) + ' found: ' + str(len(script)))
        with open('scripts/' + count + '.csv', 'w') as csvfile:
            fieldnames = ['character', 'dialogue']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            headers = dict( (n,n) for n in fieldnames )
            writer.writerow(headers)
            for line in script:
                writer.writerow({
                    'character': line[0].strip(),
                    'dialogue': line[1].strip()
                    })
        
        min_trans += 1