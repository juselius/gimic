#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:syntax=python
#
# getkw -- a simple input parser for Fortran 95
#
# Written by Jonas Juselius <jonas.juselius@chem.uit.no> 
# University of Tromsø, 2006
#
# TODO: syntax callbacks
#

import sys,os,inspect
import re, string
from copy import deepcopy
from pyparsing import \
	Literal, Word, ZeroOrMore, Group, Dict, Optional, removeQuotes, \
	printables, ParseException, restOfLine, alphas, alphanums, nums, \
	pythonStyleComment, oneOf, quotedString, SkipTo, Forward, \
	commaSeparatedList, OneOrMore, Combine, srange, delimitedList, \
    downcaseTokens

verbose=True
strict=True

class Section:
	def __init__(self,name,arg=None,req=False,multi=False):
		self.name=name
		self.sect={}
		self.kw={}
		self.arg=None
		self.req=req
		self.multi=multi
		self.set=False
		if arg is not None:
			self.set_kwarg(arg)

	def validate(self,path=None):
		dlm=''
		if path is None:
			path=''
		else:
			path=path+dlm+self.name
			dlm='.'
		if self.req and not self.set:
			print '>>> Required section not set: %s \n' % (path)
			sys.exit(0)
		if self.arg is not None:
			self.arg.validate(path)
		for i in self.kw:
			if len(self.kw[i]) > 1 and not self.kw[i][0].multdef():
				print '>>> Mulitply defined key: %s ' % (path+'.'+i)
				if strict:
					sys.exit(1)
			for j in self.kw[i]:
				j.validate(path)
		for i in self.sect:
			if len(self.sect[i]) > 1 and not self.sect[i].multdef():
				print '>>> Mulitply defined section: %s ' % (path+'.'+i)
				if strict:
					sys.exit(1)
			for j in self.sect[i]:
				j.validate(path)

	def __cmp__(self, other):
		return cmp(self.name,other.name)

	def required(self):
		return self.req

	def multdef(self):
		return self.multi

	def arg_required(self):
		if arg is None:
			return False
		return self.arg.required()

	def add_sect(self, sect, set=False):
		if not self.sect.has_key(sect.name):
			self.sect[sect.name]=[]
		sect.set=set
		self.sect[sect.name].append(sect)

	def add_kwkw(self, kw, set=False):
		if not self.kw.has_key(kw.name):
			self.kw[kw.name]=[]
		kw.set=set
		self.kw[kw.name].append(kw)

	def add_kw(self, name, typ, arg, req=False, multi=False, set=False):
		if not self.kw.has_key(name):
			self.kw[name]=[]
		kw=Keyword(name,typ,arg,req,multi)
		kw.set=set
		self.kw[name].append(kw)

	def set_kwarg(self, kw, set=False):
		if isinstance(kw,Keyword):
			kw.set=set
			self.arg=kw
		else:
			raise TypeError

	def set_arg(self, typ, arg, req=False, set=False):
		kw=Keyword(self.name,typ,arg,req)
		kw.set=set
		self.arg=kw

	def findkw(self, name):
		if self.kw.has_key(name):
			return self.kw[name][0]
		return None

	def setkw(self, name, arg):
		if self.kw.has_key(name):
			self.kw[name][0].setkw(arg)
		else:
			print 'invalid kw: ', name

	def findsect(self, name):
		if self.sect.has_key(name):
			return self.sect[name][0]
		return None

	def getsect(self, name):
		if self.sect.has_key(name):
			return self.sect[name][0]
		return None

	def get_keys(self):
		return self.kw

	def get_sects(self):
		return self.sect

	def get_arg(self):
		return self.arg

	def status(self):
		return self.set
	
	def set_status(self, set):
		if set:
			self.set=True
		else:
			self.set=False

	def sanitize(self, templ):
		self.equalize(templ)
		self.xvalidate(templ)

	# add missing keys.
	def equalize(self, templ):
		for i in templ.kw:
			if not self.kw.has_key(i):
				self.kw[i]=templ.kw[i]
		for i in templ.sect:
			if not self.sect.has_key(i):
				self.sect[i]=templ.sect[i]
			for j in self.sect[i]:
				j.equalize(templ.sect[i][0])

	#cross-validate against a template
	def xvalidate(self,templ,path=None):
		dlm=''
		if path is None:
			path=''
		else:
			path=path+dlm+self.name
			dlm='.'
		if templ.req and not self.set:
			print '>>> Required section not set: %s \n' % path
			sys.exit(1)
		self.xvalidate_arg(templ.arg,path)
		for i in self.kw:
			j=templ.findkw(i) 
			if j is None:
				print '>>> Invalid keyword: %s ' % (path+dlm+i)
				sys.exit(1)
			if len(self.kw[i]) > 1 and not j.multdef():
				print '>>> Mulitply defined key: %s ' % (path+dlm+i)
				if strict:
					sys.exit(1)
			for k in self.kw[i]:
				k.xvalidate(j,path)
		for i in self.sect:
			j=templ.findsect(i) 
			if j is None:
				print '>>> Invalid section: %s ' % (path+dlm+i)
				sys.exit(1)
			if len(self.sect[i]) > 1 and not j.multdef():
				print '>> Multiply defined section: %s ' % (path+dlm+i)
				if strict:
					sys.exit(1)
			for k in self.sect[i]:
				k.xvalidate(j,path)
				
		
	def xvalidate_arg(self,templ,path):
		kw=self.arg
		if templ is not None:
			if kw is not None:
				kw.xvalidate(templ)
			elif templ.req:
				print '>>> Required arg not set: %s \n' % (path+
						'.'+kw.name)
				sys.exit(1) # return state...
		elif kw is not None:
			print '>>> Invalid argument: %s ' % (path+'.'+kw.name)
			sys.exit(1)

	def __str__(self):
		nsect=0
		for i in self.sect:
			nsect=nsect+len(self.sect[i])
		nkw=0
		for i in self.kw:
			nkw=nkw+len(self.kw[i])
		s="SECT %s %d %s\n" % (self.name, nsect, self.set)
		if self.arg is not None:
			s=s+"ARG T KW %d\n" % (nkw)
			s=s+str(self.arg)
		else:
			s=s+"ARG F KW %d\n" % (nkw)

		for i in self.kw.values():
			for j in i:
				s=s+str(j)
		for i in self.sect.values():
			for j in i:
				s=s+str(j)
		return s
		
class Keyword:
	ival=re.compile(r'[-]?\d+$')
	dval=re.compile(r'-?\d+\.\d*([dDeE][+-]?\d+)?',re.I)
	lval=re.compile(r'(0|1|yes|no|true|false|on|off)',re.I)
	yes=re.compile(r'(1|yes|true|on)',re.I)
	no=re.compile(r'(0|no|false|off)',re.I)

	def __init__(self, name, typ, arg, req=False, multi=False):
		self.name=name
		self.type=typ
		self.req=req
		self.multi=multi
		self.nargs=None
		self.arg=[]
		if arg is None: # unlimited arg length
			self.nargs=-1
			arg=None
		elif isinstance(arg,int): # number of elements in self.arg == arg
			self.nargs=arg  
			arg=None
		if isinstance(arg,tuple) or isinstance(arg,list):
			self.nargs=len(arg)
		self.setkw(arg)
		self.set=False
#        print self

	def __cmp__(self, other):
		return cmp(self.name,other.name)
	
	def setkw(self, arg):
		if isinstance(arg,tuple):
			pass
		elif isinstance(arg,list):
			arg=tuple(arg)
		else:
			arg=(arg,)

		if arg[0] is None: # init stage
			self.arg=[]
			return

		if self.nargs > 0: 
			if len(arg) != self.nargs:
				print "keyword lenght mismatsh %s(%i): %i" % (self.name,
						self.nargs, len(arg))
				sys.exit(1)
		# store everyting as strings internally
		self.arg=[]
		for i in arg:
			self.arg.append(str(i))
		try:
			self.sanity()
		except TypeError:
			print 'Invalid argument:', arg
			sys.exit(1)
		self.set=True

	def validate(self,path):
		if path is None:
			path=self.name
		else:
			path=path+'.'+self.name
		if self.req  and not self.set:
			print '>>> Required key not set: %s \n' % (path)
			if strict:
				sys.exit(1)

	def xvalidate(self,templ,path=None):
		if path is None:
			path=self.name
		else:
			path=path+'.'+self.name
		if templ.req and not self.set:
			print '>>> Required key not set: %s \n' % (path)
			sys.exit(1)
		if templ.type != self.type:
			print '>>> Invalid data type in: %s \n' % (path)
			sys.exit(1)
		if self.nargs < 0:  #  < 0 == unlimited arg length
			if len(templ.arg) != len(self.arg):
				print '>>> Invalid data length in: %s \n' % (path)
				sys.exit(1)
		return True
				
	def sanity(self):
		if self.arg[0] == 'None':
			return True
		if (self.type == 'INT' or self.type == 'INT_ARRAY'):
			for i in self.arg:
				if not self.ival.match(i):
					print 'getkw: not an integer: ', self.name, '=',i
					raise TypeError
		elif (self.type == 'DBL' or self.type == 'DBL_ARRAY'):
			for i in self.arg:
				if not self.dval.match(i):
					print 'not a real: ', self.name, '=',i
					raise TypeError
		elif (self.type == 'BOOL' or self.type == 'BOOL_ARRAY'):
			for i in range(len(self.arg)):
				if not self.lval.match(self.arg[i]):
					print 'not a bool: ', self.name, '=',self.arg[i]
					raise TypeError
				if self.yes.match(self.arg[i]):
					self.arg[i]='True'
				elif self.no.match(self.arg[i]):
					self.arg[i]='False'
		elif self.type == 'STR':
			tmp=self.arg
			self.arg=[]
			for i in tmp:
				if len(i.strip()) != 0:
					self.arg.append(i)
			return True
		else:
			print 'unknown type: ', self.name, '=', self.type
			raise TypeError
		return True

	def multdef(self):
		return self.multi

	def required(self):
		return self.req

	def status(self):
		return self.set
	
	def set_status(self, set):
		if set:
			self.set=True
		else:
			self.set=False

	def __str__(self):
		if self.type == 'STR' and self.arg == []: # empty string
			nargs=-1 # flags as empty for Fortran code
		else:
			nargs=len(self.arg)
		s="%s %s %d %s\n" % (self.type, self.name, nargs, self.set)
		if self.arg != []:
			for i in self.arg:
				s=s+str(i)+'\n'
		return s

class GetkwParser:
	ival=re.compile(r'[-]?\d+$')
	dval=re.compile(r'-?\d+\.\d*([dDeE][+-]?\d+)?',re.I)
	lval=re.compile(r'(0|1|yes|no|true|false|on|off)',re.I)
	yes=re.compile(r'(1|yes|true|on)',re.I)
	no=re.compile(r'(0|no|false|off)',re.I)
	bnf=None
	caseless=False

	def __init__(self):
		self.top=Section('start')
		self.stack=[self.top]
		self.cur=self.stack[0]
		if GetkwParser.bnf == None:
			GetkwParser.bnf=self.getkw_bnf()
		self.parseString=self.bnf.parseString
	
	def set_caseless(self, arg):
		if arg is True:
			self.caseless=True
		else:
			self.caseless=False
	
	def parseFile(self,fil):
		self.bnf.parseFile(fil)
		return self.top
	
	def newSect(self,s,l,t):
		q=t.asList()
		name=q[0]
		if self.caseless:
			name=name.lower()
		if q[1] != []:
			arg=q[1]
			argt=self.argtype(arg)
			kw=Keyword(name, argt, arg)
		else:
			kw=None
		k=Section(name)
		if kw is not None:
			k.set_kwarg(kw, set=True)
		self.cur.add_sect(k, set=True)  
		self.pushSect(k)

	def new_aSect(self,s,l,t):
		q=t.asList()
		name=q[0]
		if self.caseless:
			name=name.lower()
		if q[1] != []:
			arg=q[1]
			argt=self.array_type(arg)  #should check consistency of all elms
			kw=Keyword(name, argt, arg)
		else:
			kw=None
		k=Section(name)
		if kw is not None:
			k.set_kwarg(kw, set=True)
		self.cur.add_sect(k, set=True)  
		self.pushSect(k)
	
	def pushSect(self,k):
		self.stack.append(k)
		self.cur=self.stack[-1]

	def popSect(self,s,l,t):
		del self.stack[-1]
		self.cur=self.stack[-1]
	
	def store_key(self,s,l,t):
		q=t.asList()
		name=q[0]
		arg=q[1]
		if self.caseless:
			name=name.lower()
		argt=self.argtype(arg)
		k=Keyword(name,argt,arg)
		self.cur.add_kwkw(k,set=True)

	def store_array(self,s,l,t):
		q=t.asList()
		name=q[0]
		arg=q[1]
		if self.caseless:
			name=name.lower()
		argt=self.array_type(arg[0])
		k=Keyword(name,argt,arg)
		self.cur.add_kwkw(k,set=True)
	
	def array_type(self,arg):
		if self.ival.match(arg):
			return 'INT_ARRAY'
		if self.dval.match(arg):
			return 'DBL_ARRAY'
		if self.lval.match(arg):
			return 'BOOL_ARRAY'
		return 'STR' #maybe introduce STR_ARRAY for consistency...

#bug! wrong type can easily be returned!
	def argtype(self,arg):
		if self.ival.match(arg):
			return 'INT'
		if self.dval.match(arg):
			return 'DBL'
		if self.lval.match(arg):
			return 'BOOL'
		return 'STR'

	def store_data(self,s,l,t):
		name=t[0]
		if self.caseless:
			name=name.lower()
		dat=t[1].split('\n')
		arg=[]
		for i in dat:
			arg.append(i.strip())
		k=Keyword(name,'STR',arg)
		self.cur.add_kwkw(k,set=True)

	def getkw_bnf(self):
		lcb  = Literal("{").suppress()
		rcb  = Literal("}").suppress()
		lsb  = Literal("[").suppress()
		rsb  = Literal("]").suppress()
		lps  = Literal("(").suppress()
		rps  = Literal(")").suppress()
		eql  = Literal("=").suppress()
		dmark=Literal('$').suppress()
		end_sect=rcb
		end_data=Literal('$end').suppress()
		prtable = srange("[0-9a-zA-Z]")+'!$%&*+-./<>?@^_|~'

		str=Word(prtable) ^ quotedString.setParseAction(removeQuotes)

		name = Word(alphas+"_",alphanums+"_")
		
		vec=lsb+delimitedList(Word(prtable) ^ Literal("\n").suppress() ^\
				quotedString.setParseAction(removeQuotes))+rsb
#        key=str ^ vec
#        keyword = name + eql + Group(key)
		simple_keyword = name + eql + str
		array_keyword = name + eql + vec
		data=Combine(dmark+name)+SkipTo(end_data)+end_data
		data.setParseAction(self.store_data)
		s_bsect=name+Optional(Group(lps+str+rps))+lcb
		a_bsect=name+Group(lps+vec+rps)+lcb
		s_bsect.setParseAction(self.newSect)
		a_bsect.setParseAction(self.new_aSect)
		end_sect.setParseAction(self.popSect)

		bsect=Group(s_bsect ^ a_bsect)

		simple_keyword.setParseAction(self.store_key)
		array_keyword.setParseAction(self.store_array)

		section=Forward()
		input=section ^ data ^ Group(simple_keyword ^ array_keyword)

		section << bsect+ZeroOrMore(input)+rcb
		
		bnf=ZeroOrMore(input)
		bnf.ignore( pythonStyleComment )

		return bnf

def test( strng ):
	bnf = GetkwParser()
	try:
		tokens=bnf.parseString(strng)
	except ParseException, err:
		print err.line
		print " "*(err.column-1) + "^"
		print err
	print bnf.top
	return tokens

if __name__ == '__main__':
	teststr="""
title = foo
title2="fooo bar"

perturbation (apa) { 
foo=[1, 2, 3,
4,5, 6,7,8,9, 
10] 
bar=22.0
}

dalron {
	foo=1 
	uar=22 
}

verbose=yes #(yes|true|on|1)

DAlron2 {
	foo=1
	bar=1

	
	vafan(3) {
		foo=0 
	}

	$COORD
	  o 0.0 0.0 0.0
	  h 1.0 1.0 0.0
	  h -1.0 1.0 0.0
	$end
}

test(off) {
	zip=" asfasf adsf asf asfd "
	$as
		"asdf sadwa:
		asf  ddddddddddddddddddddddd"

		sdfff
		sdff
	$end
}

"""
	ini = test(teststr)
	print ini

