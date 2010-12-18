# -*- coding: cp1251 -*-
class girl:
    methods = {'и':'у','й':'ю','ти':'щу','ей':'ью','ри':'рю',
               'ери':'еру','ети':'ечу','ись':'усь','йся':'юсь',
               'оди':'ожу','рай':'раю','вись':'вюсь','тись':'чусь'}
    def __init__(self, name = 'Наташа'):
        print 'Привет, меня зовут', name
        self.name = name
    def __del__(self):
        print 'Прощай'
    def __getattr__(self, m):
        for l in xrange( len(m) ):
            try:
                print m[:l] + girl.methods[ m[l:] ]
                return
            except KeyError: pass
        if m[0] != '_': print 'Я не умею это делать'

g = girl()
print g.подходи
