import itertools
import re
import sublime
import sublime_plugin
import subprocess

#filterText
class FilterTxtCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		selected = self.view.sel()[0]
		if(selected.a != selected.b):
			#把当前选中的内容作为condition
			searchText = self.view.substr(sublime.Region(selected.a, selected.b))
			self.view.run_command('split_match_content', {"pattern":searchText, "flag":sublime.IGNORECASE|sublime.LITERAL})
		else:
			#用户手工输入condition
			self.view.window().show_input_panel("FilterTxt - match condition: ", "", self.on_done, None, None)

	def  on_done(self, condition):
		self.view.run_command('split_match_content', {"pattern":condition, "flag":sublime.IGNORECASE})

class SplitMatchContentCommand(sublime_plugin.TextCommand):
	def run(self, edit, pattern=None, flag=sublime.IGNORECASE):
		view = self.view
		searchText = pattern

		#search, group by line number for duplicate records removing
		lines = itertools.groupby(view.find_all(searchText, flag), view.line)
		lines = [l for l, _ in lines]

		regions = []
		region = None
		for line in lines:
			region = sublime.Region(line.begin(), line.end())
			#collect the all of matched records
			regions.append(region)

		printPoint = 0
		#create a new View
		newView = view.window().new_file()
		newView.set_name('FilterTxt: '+ searchText[0:10] + '...')
		for content in regions:
			#write the results of matched in new view
			count = newView.insert(edit, printPoint, view.substr(content)+'\n')
			printPoint = printPoint+count

		#hide the results of matched in old view
		view.fold(regions)

#filterCode
class FilterCodeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		selected = self.view.sel()[0]
		if(selected.a != selected.b):
			#把当前选中的内容作为condition
			searchText = self.view.substr(sublime.Region(selected.a, selected.b))
			self.view.run_command('split_match_code', {"pattern":searchText, "flag":sublime.IGNORECASE|sublime.LITERAL})
		else:
			#用户手工输入condition
			self.view.window().show_input_panel("FilterCode - match condition: ", "", self.on_done, None, None)

	def  on_done(self, condition):
		self.view.run_command('split_match_code', {"pattern":condition, "flag":sublime.IGNORECASE})

class SplitMatchCodeCommand(sublime_plugin.TextCommand):
	def run(self, edit, pattern=None, flag=sublime.IGNORECASE):
		view = self.view
		searchText = pattern

		#search, group by line number for duplicate records removing
		lines = itertools.groupby(view.find_all(searchText, flag), view.line)
		lines = [l for l, _ in lines]

		fileNameRegions = []
		foldRegions = []
		codeRegions = []
		lastRegions= [] #用于判断是否有重复的Regions
		region = None
		for line in lines:
			region = sublime.Region(line.begin(), line.end())
			#collect the all of matched records
			foldRegions.append(region)

			#获取匹配项对应的文件名
			fileNameRegion = CommonUtils.getBelongFileName(self, line.begin())
			if(fileNameRegion is not None):
				if fileNameRegion not in fileNameRegions:
					fileNameRegions.append(fileNameRegion)
					codeRegions.append(fileNameRegion)

			#collect all of matched records and related context
			upStep = 20
			downStep = 20
			regionsWithContext = self.getRelatedCodeByPoint(line.begin(), fileNameRegion, upStep, downStep)
			#检查相邻2个的重复region段，避免重复打印
			isSame = False
			if len(lastRegions) != 0 and self.compareRegions(regionsWithContext, lastRegions) == True:
				isSame = True
			else:
				isSame = False

			lastRegions = []
			for content in regionsWithContext:
				if isSame==False:
					codeRegions.append(content)
				lastRegions.append(content)

		printPoint = 0
		code = ''
		#create a new View
		newView = view.window().new_file()
		newView.set_name('FilterCode: '+ searchText[0:10] + '...')

		for content in codeRegions:
			#recogonize the filename or content
			record  = view.substr(content)
			if(content in fileNameRegions):
				#insert a new line when it is filename
				code = '\n' + record + '\n'
			else:
				code = record + '\n'
			#write the results of matched in new view
			count = newView.insert(edit, printPoint, code)
			printPoint = printPoint+count

		#hide the results of matched in old view
		view.fold(foldRegions)

	#get context and filename of current line
	def getRelatedCodeByPoint(self, point, fileNameRegion, upStep=2, downStep=2):
		#current line
		currentLine = self.view.line(point)

		#get more lines to little linenumber direction
		upRegions = self.getMoreLine(point, fileNameRegion, upStep, 0)
		#get more lines to big linenumber direction
		downRegions = self.getMoreLine(point, None, downStep, 1)

		#combined the context of matched line
		regions = []
		for content in upRegions[::-1]:
			if content is not None:
				regions.append(content)
		if fileNameRegion != currentLine:
			regions.append(currentLine)
		for content in downRegions:
			if content is not None:
				regions.append(content)
		return regions

	def getMoreLine(self, point, fileNameRegion=None, lineNumber=2, direct=0):
		regions=[]
		lastLineIsFileName = False
		currentLine =self.view.line(point)
		for currentTime in range(lineNumber):
			if 0==direct:
				#up direction
				nextLine = self.view.line(currentLine.begin()-1)
			else:
				#down direction
				nextLine = self.view.line(currentLine.end()+1)

			if nextLine.begin()>self.view.size() or nextLine.end()>self.view.size() or nextLine.begin()<0:
				break
			if fileNameRegion is not None and 0==direct:
				#if content of current line is filename, the list not add it.
				if fileNameRegion != nextLine:
					if self.view.substr(nextLine) != '' or lastLineIsFileName == False:
						regions.append(nextLine)
					lastLineIsFileName = False
				else:
					lastLineIsFileName = True
			else:
				regions.append(nextLine)
			currentLine = self.view.line(nextLine)
			nextContent = self.view.substr(nextLine).strip()
			if ''== nextContent or None == nextContent:
				break
			match = CommonUtils.expressionMatch(nextContent, r'^[. ]+$')
			if match:
				break
		return regions

	#get related filename of matched line
	# def getBelongFileName(self, point):
	# 	#current line
	# 	currentLine = self.view.line(point)

	# 	#regular expression of filename
	# 	patternFileName = r'^[a-zA-Z]:[\\\S ]+'
	# 	while currentLine.begin() >= 0:
	# 		fileName = self.view.substr(currentLine).strip()
	# 		#if null line, return directly
	# 		if fileName == '':
	# 			return currentLine
	# 		match = CommonUtils.expressionMatch(fileName, patternFileName)
	# 		if match:
	# 			return currentLine
	# 		else:
	# 			currentLine = self.view.line(currentLine.begin()-1)
	# 	return None

	#match regular expression
	# def expressionMatch(self, content, patternStr):
	# 	pattern = re.compile(patternStr)
	# 	match = pattern.match(content)
	# 	return match

	def compareRegions(self, newRegions, oldRegions):
		if len(newRegions)==0 or len(oldRegions) ==0:
			return False
		newSize = len(newRegions)
		oldSize = len(oldRegions)
		if newSize== oldSize:
			for index in range(newSize):
				newR = newRegions[index]
				oldR = oldRegions[index]
				if newR.begin() == oldR.begin() and newR.end() == oldR.end():
					continue
				else:
					return False
		else:
			return False
		return True

class FilterCodeDoubleClickCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("demo print"+self.view.name())
		if self.view.name().startswith("FilterCode:") or self.view.name().startswith("FilterTxt:"):
			selected = self.view.sel()[0]
			line = self.view.substr(self.view.line(selected.a))
			pattern = r'^[\s\d]+'
			match = CommonUtils.expressionMatch(line, pattern)
			#get line number
			lineNo = int(match.group(0).strip())

			fileNameRegion = CommonUtils.getBelongFileName(self, selected.a)
			if fileNameRegion is None:
				return
			else:
				fileName = self.view.substr(fileNameRegion)
				if fileName.endswith(":"):
					fileName = fileName.rstrip(':')
					self.view.window().open_file("%s:%s" % (fileName, lineNo), sublime.ENCODED_POSITION)

class CommonUtils(object):
	#match regular expression
	@staticmethod
	def expressionMatch(content, patternStr):
		pattern = re.compile(patternStr)
		match = pattern.match(content)
		return match

	#get related filename of matched line
	@staticmethod
	def getBelongFileName(self, point):
		#current line
		currentLine = self.view.line(point)

		#regular expression of filename
		patternFileName = r'^[a-zA-Z]:[\\\S ]+'
		while currentLine.begin() >= 0:
			fileName = self.view.substr(currentLine).strip()
			#if null line, return directly
			if fileName == '':
				return currentLine
			match = CommonUtils.expressionMatch(fileName, patternFileName)
			if match:
				return currentLine
			else:
				currentLine = self.view.line(currentLine.begin()-1)
		return None