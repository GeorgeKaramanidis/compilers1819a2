import plex

class ParseError(Exception):
	pass

class MyParser:
	def __init__(self):
		space = plex.Any(" \n\t")
		brackets = plex.Str('(',')')
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		name = letter+plex.Rep(letter|digit)
		bit = plex.Range('01')
		bits = plex.Rep1(bit)
		keyword = plex.Str('print','PRINT')
		space = plex.Any(" \n\t")
		operator=plex.Str('=','xor','or','and')
		
		self.lexicon = plex.Lexicon([
			(operator,plex.TEXT),
			(bits, 'BIT_TOKEN'),
			(keyword,'PRINT'),
			(brackets,plex.TEXT),
			(name,'IDENTIFIER'),
			(space,plex.IGNORE)
			])

	def create_scanner(self,fp):
		self.scanner = plex.Scanner(self.lexicon,fp)
		self.la,self.text=self.next_token()

	def next_token(self):
		return self.scanner.read()

	def match(self,token):
		if self.la == token:
			self.la,self.text=self.next_token()
		else:
			raise ParseError("Expected (")

	def parse(self,fp):
		self.create_scanner(fp)
		self.stmt_list()
		
	def stmt_list(self):
		if self.la == 'IDENTIFIER' or self.la == 'PRINT':
			self.stmt()
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("Expected IDENTIFIER or Print")
	
	def stmt(self):
		if self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')	
			self.match('=')
			self.exp()
		elif self.la == 'PRINT':
			self.match('PRINT')
			self.exp()
		else:
			raise ParseError("Expected IDENTIFIER or PRINT")
	
	def exp(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			self.term()
			self.term_tail()
		else:
			raise ParseError("Expected ( or IDENTIFIER or BIT_TOKEN or )")
	
	def term_tail(self):	
		if self.la == 'xor':
			self.match('xor')
			self.term()
			self.term_tail()
		elif self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected xor")

	def term(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':	
			self.factor()
			self.factor_tail()
		else:
			raise ParseError("Expected ( or IDENTIFIER or )")

	def factor_tail(self):
		if self.la == 'or':
			self.match('or')
			self.factor()
			self.factor_tail()
		elif self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected or")

	def factor(self):
		if self.la == '(' or self.la == 'IDENTIFIER' or self.la == 'BIT_TOKEN':
			self.atom()
			self.atom_tail()
		else:
			raise ParseError("Expected id,bit h (")

	def atom_tail(self):
		if self.la == 'and':
			self.match('and')
			self.atom()
			self.atom_tail()
		elif self.la == 'or' or self.la == 'xor' or self.la == 'IDENTIFIER' or self.la == 'PRINT' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected and")

	def atom(self):
		if self.la == '(':
			self.match('(')
			self.exp()
			self.match(')')
		elif self.la == 'IDENTIFIER':
			self.match('IDENTIFIER')
		elif self.la == 'BIT_TOKEN':
			self.match('BIT_TOKEN')
		else:
			raise ParseError("Expected id bit or (")

parser = MyParser()

with open('text.txt','r') as fp:
	parser.parse(fp)