#!/usr/bin/env python
# coding: utf-8

import re


def parse_hunk_meta(hunk_meta):
    # @@ -3,7 +3,6 @@
    a = hunk_meta.split()[1].split(',')   # -3 7
    if len(a) > 1:
        old_addr = (int(a[0][1:]), int(a[1]))
    else:
        # @@ -1 +1,2 @@
        old_addr = (int(a[0][1:]), 0)

    b = hunk_meta.split()[2].split(',')   # +3 6
    if len(b) > 1:
        new_addr = (int(b[0][1:]), int(b[1]))
    else:
        # @@ -0,0 +1 @@
        new_addr = (int(b[0][1:]), 0)

    return old_addr, new_addr


def get_block_generator(lines):
    block = {
        'old_path': None,
        'new_path': None,
        'hunks': []
    }

    for line in lines:
        t_line = line

        if line.startswith('---'):
            if block['old_path'] and block['new_path'] and block['hunks']:
                yield block
            block = {
                'old_path': line,
                'new_path': None,
                'hunks': []
            }

        elif line.startswith('+++') and block['old_path']:
            block['new_path'] = line

        elif line.startswith('@@') \
                or (line.startswith('+') and not line.startswith('+++')) \
                or (line.startswith('-') and not line.startswith('---')) \
                or line.startswith(' '):
            block['hunks'].append(line)

        else:
            block['hunks'].append(line)

    if block['old_path'] and block['new_path']:
        if len(block['hunks']) > 0:
            yield block


class Plugin(object):
    info = {
        'name': 'Sample Reflected XSS Match',
        'tag': 'xss'
    }

    rules = [
        {'desc': 'htmlspecialchars()匹配规则触发',
         'rule': r'= .*htmlspecialchars(.*?)'},
        {'desc': 'others',
         'rule': r'asjfkalsjdflkajsdklfjasldkfj'}
    ]

    def scan(self, raw_content):
        result = {}
        reports = []

        for rule in self.rules:
            blocks = get_block_generator(raw_content.split('\n'))
            for block in blocks:
                current_meta = None
                index = 0
                r_index = 0
                o_offset = 0
                n_offset = 0
                for line in block['hunks']:
                    index += 1
                    if line.startswith('@@'):
                        current_meta = line
                        r_index = 0
                        o_offset = 0
                        n_offset = 0
                        continue

                    if re.search(rule['rule'], line) and \
                            (line.startswith('+') or line.startswith('-')):
                        old_addr, new_addr = parse_hunk_meta(current_meta)
                        linemeta = '%dn (old) | %dn (new)   [%d]' \
                                   % ((old_addr[0] + r_index + o_offset),
                                      (new_addr[0] + r_index + n_offset),
                                      index)
                        # linemeta = '%d-%d (old) | %d-%d (new)' \
                        #            % (old_addr[0], old_addr[0] + old_addr[1],
                        #               new_addr[0], new_addr[0] + new_addr[1])
                        report = {
                            'file': block['old_path'][4:],  # "--- lib/core.php" to "lib/core.php"
                            'line': linemeta,
                            'desc': rule['desc']
                        }
                        reports.append(report)

                    if line.startswith('+'):
                        n_offset += 1
                    elif line.startswith('-'):
                        o_offset += 1
                    else:
                        r_index += 1

        result['name'] = self.info['name']
        result['tag'] = self.info['tag']
        result['reports'] = reports

        return result
