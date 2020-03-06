"""
 This class holds arrays of the file paths of the memes so we are able to fetch specific meme types.

 The meme_meta.json MUST NOT BE EMPTY!!! However, the FILE_ID may be blank. It is fetched after the first upload.

 It has this file structure:

 {
	"COURSE1": {
		"TYPE1": {
			"MEME1": [
				"PATH",
				"FILE_ID"
			],
			"MEME2": [
				"PATH",
				""
			]
	  	},
	  	"TYPE2": {
			"MEME1": [
				"PATH",
				""
			]
	  	}
  	}
}
"""
import random
import json


class Memes:
	def __init__(self):
		self.memeTypes = self.readMemeTypes()

	# self.memeTypes = self.readMemeTypes()

	# Get a meme of a specific type and with a specific identifier.
	# If type and meme are left blank, a random meme is returned.
	# If only meme is blank, a random meme of this type is returned.
	# list(DICTNAME)[INDEX] returns the key at this index
	def getMeme(self, course, type, meme):
		if type == '-1':
			if meme == '-1':
				# Generate random type and meme indices
				typeIndex = random.randrange(len(self.memeTypes[course]))
				typeKeys = list(self.memeTypes[course])
				memeIndex = random.randrange(len(self.memeTypes[course][typeKeys[typeIndex]]))

				# Fetch the meme
				memeSource = self.getMemeSourceList(course, typeIndex, memeIndex)

				return self.returnMeme(memeSource, typeIndex, memeIndex)
		else:
			if meme == '-1':
				typeIndex = list(self.memeTypes[course]).index(type)
				memeIndex = random.randrange(len(self.memeTypes[course][type]))

				memeSource = self.getMemeSourceList(course, typeIndex, memeIndex)

				return self.returnMeme(memeSource, typeIndex, memeIndex)
			else:
				typeIndex = list(self.memeTypes[course]).index(type)
				memeIndex = list(self.memeTypes[course][type]).index(meme)

				memeSource = self.getMemeSourceList(course, typeIndex, memeIndex)

				return self.returnMeme(memeSource, typeIndex, memeIndex)

	def returnMeme(self, meme, typeIndex, memeIndex):
		# If the file_id of the meme is already known, return the id. Otherwise return the file itself.
		if meme[1] != '':
			return [meme[1], False, typeIndex, memeIndex]
		else:
			# Return the meme file, the boolean that we need the id, the type and the meme so its easier to find the
			# meme in the addMemeId method.
			return [open(meme[0], 'rb'), True, typeIndex, memeIndex]

	# Returns a list with all available meme types
	def getMemeTypes(self, course):
		return list(self.memeTypes[course])

	# Returns a list with all available memes for a given type
	def getMemeId(self, course, type):
		if type in self.memeTypes[course]:
			return list(self.memeTypes[course][type])
		else:
			return ['/help']

	def addMemeId(self, course, typeIndex, memeIndex, file_id):
		self.getMemeSourceList(course, typeIndex, memeIndex)[1] = file_id

		with open('memes/meme_meta.json', 'w')as memeFile:
			memeFile.write(json.dumps(self.memeTypes))

	def readMemeTypes(self):
		try:
			with open('memes/meme_meta.json', 'r') as memeFile:
				memeJson = memeFile.read()
			memeFile.close()

			return json.loads(memeJson)

		except:
			with open('memes/meme_meta.json', 'w') as memeFile:
				memeFile.close()

	# Returns the list with path and id of the meme
	def getMemeSourceList(self, course, typeIndex, memeIndex):
		memeType = list(self.memeTypes[course])[typeIndex]
		memesOfThisType = self.memeTypes[course][memeType]
		meme = memesOfThisType[list(memesOfThisType)[memeIndex]]

		return meme

	# Returns the access password for a given course
	def getPassword(self, course):
		return self.memeTypes['PASSWORDS'][course]

	def setPassword(self, course, password):
		self.memeTypes['PASSWORDS'][course] = password

		with open('memes/meme_meta.json', 'w')as memeFile:
			memeFile.write(json.dumps(self.memeTypes))
