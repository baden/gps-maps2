# -*- coding: cp1251 -*-
class girl:
    methods = {'�':'�','�':'�','��':'��','��':'��','��':'��',
               '���':'���','���':'���','���':'���','���':'���',
               '���':'���','���':'���','����':'����','����':'����'}
    def __init__(self, name = '������'):
        print '������, ���� �����', name
        self.name = name
    def __del__(self):
        print '������'
    def __getattr__(self, m):
        for l in xrange( len(m) ):
            try:
                print m[:l] + girl.methods[ m[l:] ]
                return
            except KeyError: pass
        if m[0] != '_': print '� �� ���� ��� ������'

g = girl()
print g.�������
