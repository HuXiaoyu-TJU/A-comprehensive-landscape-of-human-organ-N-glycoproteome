# -*- coding: utf-8 -*-
"""
Created on Wed Jan 19 00:35:24 2022

@author: Tenmty
"""
'''
file = open('struct_conv_monosaccharides.gpc', 'r', encoding = 'UTF-8')
monosacharride_list = file.readline().strip('\n').split(',')
pGlyco_list = file.readline().strip('\n').split(',')
gwb_list = file.readline().strip('\n').split(',')
file.close()
del file

series = range(len(monosacharride_list))
monosaccharide_coding = dict(zip(monosacharride_list, series))
pGlyco_coding = {}
for i in series: pGlyco_coding.setdefault(pGlyco_list[i], i)
gwb_coding= dict(zip(gwb_list, series))
monosaccharide_decoding = dict(zip(series, monosacharride_list))
pGlyco_decoding = dict(zip(series, pGlyco_list))
gwb_decoding = dict(zip(series, gwb_list))
del series
'''

def parse_GPSeeker_linkage(linkage, monosaccharide_coding):
    dec_struct = {0: {(0, 0, 0): []}}
    current_grade = 0
    current_antenna = (0, 0, 0)
    unknown_count = -len(linkage.replace('(', '').replace(')', '')) // 3 * 2 - 1
    last_char = '0'
    for code in linkage[1:]:
        if 47 < ord(code) < 58:
            num = int(code)
            overlapped = False
            if 47 < ord(last_char) < 58 or last_char == '?':
                dec_struct[current_grade][current_antenna].append([num])
                last_char = code
            elif last_char == '(':
                branch_mono = dec_struct[current_grade - 1][current_antenna][-1]
                if num == branch_mono[0] or num in branch_mono[2:]:
                    overlapped = True
                branch_mono.append(num)
                current_antenna = (current_antenna, len(dec_struct[current_grade - 1][current_antenna]) - 1, num)
                dec_struct[current_grade][current_antenna] = []
                last_char = code
            else:
                last_mono = dec_struct[current_grade][current_antenna][-1]
                if num == last_mono[0] or num in last_mono[2:]:
                    overlapped = True
                last_mono.append(num)
                last_char = code
            if overlapped:
                raise Exception('Invalid glycan structure perceived.')
        elif code == '?':
            num = unknown_count
            unknown_count += 1
            if 47 < ord(last_char) < 58 or last_char == '?':
                dec_struct[current_grade][current_antenna].append([num])
                last_char = code
            elif last_char == '(':
                dec_struct[current_grade - 1][current_antenna][-1].append(num)
                current_antenna = (current_antenna, len(dec_struct[current_grade - 1][current_antenna]) - 1, num)
                dec_struct[current_grade][current_antenna] = []
                last_char = code
            else:
                dec_struct[current_grade][current_antenna][-1].append(num)
                last_char = code
        elif code == '(':
            current_grade += 1
            dec_struct.setdefault(current_grade, {})
            last_char = code
        elif code == ')':
            current_grade -= 1
            current_antenna = current_antenna[0]
            last_char = code
        else:
            try:
                dec_struct[current_grade][current_antenna][-1].append(monosaccharide_coding[code])
            except:
                raise Exception('Undefined monosaccharide %s perceived.'%code)
            last_char = code
    return dec_struct


def parse_pGlyco_linkage(linkage, pGlyco_coding):
    if linkage.count('(') != linkage.count(')'): raise Exception('Invalid glycan structure perceived.')
    dec_struct = {0: {(0, 0, 0): []}}
    current_grade = 0
    current_antenna = (0, 0, 0)
    mono_check_points = {0:0}
    last_code = '('
    unknown_count = -1
    for code in linkage[1:]:
        if code == '(':
            if last_code != ')':
                dec_struct[current_grade][current_antenna][-1].append(unknown_count)
                unknown_count -= 1
                mono_check_points[current_grade] += 1
            else:
                dec_struct[current_grade][current_antenna][mono_check_points[current_grade]].insert(2, unknown_count)
                current_antenna = (current_antenna, mono_check_points[current_grade], unknown_count)
                unknown_count -= 1
                current_grade += 1
                mono_check_points[current_grade] = 0
                dec_struct.setdefault(current_grade, {})
                dec_struct[current_grade].setdefault(current_antenna, [])
            last_code = code
        elif code == ')':
            if mono_check_points[current_grade] <= 0:
                current_grade -= 1
                current_antenna = current_antenna[0]
            else:
                mono_check_points[current_grade] -= 1
            last_code = code
        else:
            try:
                dec_struct[current_grade][current_antenna].append([unknown_count, pGlyco_coding[code]])
                unknown_count -= 1
            except:
                raise Exception('Undefined monosaccharide %s perceived.'%code)
            last_code = code
    return dec_struct


def parse_GWB_linkage(linkage, gwb_coding):
    dec_struct = {0: {(0, 0, 0): [[]]}}
    current_grade = 0
    current_antenna = (0, 0, 0)
    remained_branch = {0:0}
    info = linkage.split('$')
    unknown_count = -info[0].count('--') * 2 - 1
    lk = info[0].split('--')
    last_grade = 0
    last_mono = lk[0]
    freeEnd_removed = False
    for mono in lk[1:]:
        link = mono[:3]
        monosaccharide = mono[3:].rstrip('()')
        l_link = int()
        r_link = int()
        mono_code = int()
        try:
            l_link = int(link[0])
        except:
            l_link = unknown_count
            unknown_count += 1
        try:
            r_link = int(link[-1])
        except:
            r_link = unknown_count
            unknown_count += 1
        try:
            if '-' in monosaccharide:
                if ',' in monosaccharide:
                    mono_code = gwb_coding[monosaccharide[2:-2]]
                else:
                    mono_code = gwb_coding[monosaccharide[2:]]
            else:
                if ',' in monosaccharide:
                    mono_code = gwb_coding[monosaccharide[:-2]]
                else:
                    mono_code = gwb_coding[monosaccharide]
        except:
            raise Exception('Undefined monosaccharide %s perceived.'%monosaccharide)
        if '(' in last_mono:
            last_monosaccharide = dec_struct[current_grade - 1][current_antenna][-1]
            if l_link == last_monosaccharide[0]: raise Exception('Invalid glycan structure perceived.')
            last_monosaccharide.append(l_link)
            current_antenna = (current_antenna, len(dec_struct[current_grade - 1][current_antenna]) - 1, l_link)
            dec_struct[current_grade].setdefault(current_antenna, [])
        elif ')' in last_mono:    
            if last_grade == current_grade:
                branch_mono = dec_struct[current_grade - 1][current_antenna[0]][current_antenna[1]]
                if l_link in branch_mono[2:] or l_link == branch_mono[0]: raise Exception('Invalid glycan structure perceived.')
                branch_mono.append(l_link)
                current_antenna = (current_antenna[0], current_antenna[1], l_link)
                dec_struct[current_grade].setdefault(current_antenna, [])
            else:
                current_antenna = current_antenna[0]
                branch_mono = dec_struct[current_grade][current_antenna][-1]
                if l_link in branch_mono[2:] or l_link == branch_mono[0]: raise Exception('Invalid glycan structure perceived.')
                branch_mono.append(l_link)
        else:
            last_monosaccharide = dec_struct[current_grade][current_antenna][-1]
            if freeEnd_removed and l_link == last_monosaccharide[0]: raise Exception('Invalid glycan structure perceived.')
            last_monosaccharide.append(l_link)
        if '(' in mono:         
            dec_struct[current_grade][current_antenna].append([r_link, mono_code])
            last_grade = current_grade
            last_mono = mono
            current_grade += 1
            dec_struct.setdefault(current_grade, {})
            remained_branch[current_grade] = mono.count('(')     
        elif ')' in mono:
            dec_struct[current_grade][current_antenna].append([r_link, mono_code])
            last_grade = current_grade
            last_mono = mono
            if remained_branch[current_grade] > 1:
                remained_branch[current_grade] -= 1
            else:
                remained_branch[current_grade] = 0
                current_grade -= 1
        else:
            dec_struct[current_grade][current_antenna].append([r_link, mono_code])
            last_grade = current_grade
            last_mono = mono
        if not freeEnd_removed:
            del dec_struct[0][(0, 0, 0)][0]
            freeEnd_removed = True
    return dec_struct
            

def convert_to_GPSeeker(dec_struct, monosaccharide_decoding):
    linkage = '0'
    current_grade = 0
    current_antenna = (0, 0, 0)
    mono_check_points = {}
    assigned_branches = {}
    for grade in dec_struct.keys():
        mono_check_points[grade] = 0
        assigned_branches[grade] = set()
    while True:
        mono_index = mono_check_points[current_grade]       
        monosaccharide = dec_struct[current_grade][current_antenna][mono_index]
        length = len(monosaccharide)
        if length == 3:
            if monosaccharide[0] > 0:
                if monosaccharide[2] > 0:
                    linkage += '%d%s%d'%(monosaccharide[0], monosaccharide_decoding[monosaccharide[1]], monosaccharide[2])
                else:
                    linkage += '%d%s?'%(monosaccharide[0], monosaccharide_decoding[monosaccharide[1]])
            else:
                if monosaccharide[2] > 0:
                    linkage += '?%s%d'%(monosaccharide_decoding[monosaccharide[1]], monosaccharide[2])
                else:
                    linkage += '?%s?'%monosaccharide_decoding[monosaccharide[1]]
            mono_check_points[current_grade] += 1
        elif length > 3:
            branch_locs = monosaccharide[2:-1]
            if len(assigned_branches[current_grade]) == 0:
                branch_loc = min(branch_locs)               
                if monosaccharide[0] > 0:
                    if branch_loc > 0:
                        linkage += '%d%s(%d'%(monosaccharide[0], monosaccharide_decoding[monosaccharide[1]], branch_loc)
                    else:
                        linkage += '%d%s(?'%(monosaccharide[0], monosaccharide_decoding[monosaccharide[1]])
                else:
                    if branch_loc > 0:
                        linkage += '?%s(%d'%(monosaccharide_decoding[monosaccharide[1]], branch_loc)
                    else:
                        linkage += '?%s(?'%monosaccharide_decoding[monosaccharide[1]]
                current_antenna = (current_antenna, mono_index, branch_loc)
                assigned_branches[current_grade].add(branch_loc)
                current_grade += 1
            else:
                branch_locs = set(branch_locs) - assigned_branches[current_grade]
                try:
                    branch_loc = min(branch_locs)
                    if branch_loc > 0: linkage += '(%d'%branch_loc
                    else: linkage += '(?'
                    current_antenna = (current_antenna, mono_index, branch_loc)
                    assigned_branches[current_grade].add(branch_loc)
                    current_grade += 1
                except:
                    if monosaccharide[-1] > 0: linkage += '%d'%(monosaccharide[-1])
                    else: linkage += '?'
                    assigned_branches[current_grade].clear()
                    mono_check_points[current_grade] += 1
        else:
            if monosaccharide[0] > 0: linkage += '%d%s)'%(monosaccharide[0], monosaccharide_decoding[monosaccharide[1]])
            else: linkage += '?%s)'%(monosaccharide_decoding[monosaccharide[1]])
            if current_grade == 0: break
            mono_check_points[current_grade] = 0
            current_antenna = current_antenna[0]
            current_grade -= 1
    return linkage[:-1]


def convert_to_pGlyco(dec_struct, pGlyco_decoding):
    linkage = ''
    current_grade = 0
    current_antenna = (0, 0, 0)
    mono_check_points = {}
    assigned_branches = {}
    for grade in dec_struct.keys():
        mono_check_points[grade] = 0
        assigned_branches[grade] = set()
    forward = True
    while True:
        mono_index = mono_check_points[current_grade]       
        monosaccharide = dec_struct[current_grade][current_antenna][mono_index]
        length = len(monosaccharide)
        if length == 3:
            if forward:
                linkage += '(%s'%(pGlyco_decoding[monosaccharide[1]])
                mono_check_points[current_grade] += 1
            else:
                linkage += ')'
                if mono_check_points[current_grade] == 0:
                    if current_grade == 0: break
                    elif current_antenna[2] > dec_struct[current_grade - 1][current_antenna[0]][current_antenna[1]][-1]:
                        forward = True
                    current_grade -= 1
                    current_antenna = current_antenna[0]
                else:
                    mono_check_points[current_grade] -= 1
        elif length > 3:
            branch_locs = monosaccharide[2:]
            chain_loc = monosaccharide[-1]
            branch_locs.sort()          
            if forward:
                branch_locs = branch_locs[branch_locs.index(chain_loc) + 1:]
                if len(assigned_branches[current_grade]) == 0:
                    linkage += '(%s'%(pGlyco_decoding[monosaccharide[1]])
                try:
                    branch_loc = max(set(branch_locs) - assigned_branches[current_grade])
                    current_antenna = (current_antenna, mono_index, branch_loc)
                    assigned_branches[current_grade].add(branch_loc)
                    current_grade += 1
                except:
                    mono_check_points[current_grade] += 1
                    assigned_branches[current_grade].clear()
            else:
                branch_locs = branch_locs[:branch_locs.index(chain_loc)]
                try:
                    branch_loc = max(set(branch_locs) - assigned_branches[current_grade])
                    current_antenna = (current_antenna, mono_index, branch_loc)
                    assigned_branches[current_grade].add(branch_loc)
                    current_grade += 1
                    forward = True
                except:
                    linkage += ')'
                    assigned_branches[current_grade].clear()
                    if mono_check_points[current_grade] == 0:
                        if current_grade == 0: break
                        elif current_antenna[2] > dec_struct[current_grade - 1][current_antenna[0]][current_antenna[1]][-1]:
                            forward = True
                        current_grade -= 1
                        current_antenna = current_antenna[0]
                    else:
                        mono_check_points[current_grade] -= 1
        else:
            if forward:
                linkage += '(%s'%(pGlyco_decoding[monosaccharide[1]])
                forward = False
            else:
                linkage += ')'                
                if mono_check_points[current_grade] == 0:
                    if current_grade == 0: break
                    elif current_antenna[2] > dec_struct[current_grade - 1][current_antenna[0]][current_antenna[1]][-1]:
                        forward = True
                    current_grade -= 1
                    current_antenna = current_antenna[0]
                else:
                    mono_check_points[current_grade] -= 1
    return linkage


def convert_to_GWB(dec_struct, gwb_decoding):
    linkage = 'freeEnd--?'
    current_grade = 0
    current_antenna = (0, 0, 0)
    mono_check_points = {}
    assigned_branches = {}
    for grade in dec_struct.keys():
        mono_check_points[grade] = 0
        assigned_branches[grade] = set()
    while True:
        mono_index = mono_check_points[current_grade]
        monosaccharide = dec_struct[current_grade][current_antenna][mono_index]
        length = len(monosaccharide)
        if length == 3:   
            if monosaccharide[0] > 0:
                if monosaccharide[2] > 0:
                    linkage += '?%d%s--%d'%(monosaccharide[0], gwb_decoding[monosaccharide[1]], monosaccharide[2])
                else:
                    linkage += '?%d%s--?'%(monosaccharide[0], gwb_decoding[monosaccharide[1]])
            else:
                if monosaccharide[2] > 0:
                    linkage += '??%s--%d'%(gwb_decoding[monosaccharide[1]], monosaccharide[2])
                else:
                    linkage += '??%s--?'%gwb_decoding[monosaccharide[1]]
            mono_check_points[current_grade] += 1
        elif length > 3:
            branch_locs = monosaccharide[2:-1]
            if len(assigned_branches[current_grade]) == 0:
                branch_loc = min(branch_locs)
                if monosaccharide[0] > 0:
                    if branch_loc > 0:
                        linkage += '?%d%s--%d'%(monosaccharide[0], gwb_decoding[monosaccharide[1]] + '(' * len(branch_locs), branch_loc)
                    else:
                        linkage += '?%d%s--?'%(monosaccharide[0], gwb_decoding[monosaccharide[1]] + '(' * len(branch_locs))
                else:
                    if branch_loc > 0:
                        linkage += '??%s--%d'%(gwb_decoding[monosaccharide[1]] + '(' * len(branch_locs), branch_loc)
                    else:
                        linkage += '??%s--?'%(gwb_decoding[monosaccharide[1]] + '(' * len(branch_locs))
                current_antenna = (current_antenna, mono_index, branch_loc)
                assigned_branches[current_grade].add(branch_loc)
                current_grade += 1
            else:
                branch_locs = set(branch_locs) - assigned_branches[current_grade]
                try:
                    branch_loc = min(branch_locs)
                    if branch_loc > 0: linkage += '--%d'%branch_loc
                    else: linkage += '--?'
                    current_antenna = (current_antenna, mono_index, branch_loc)
                    assigned_branches[current_grade].add(branch_loc)
                    current_grade += 1
                except:
                    if monosaccharide[-1] > 0: linkage += '--%d'%(monosaccharide[-1])
                    else: linkage += '--?'
                    assigned_branches[current_grade].clear()
                    mono_check_points[current_grade] += 1
        else:
            if monosaccharide[0] > 0: linkage += '?%d%s)'%(monosaccharide[0], gwb_decoding[monosaccharide[1]])
            else: linkage += '??%s)'%gwb_decoding[monosaccharide[1]]
            if current_grade == 0: break
            mono_check_points[current_grade] = 0
            current_antenna = current_antenna[0]
            current_grade -= 1
    return linkage[:-1]