import pandas as pd

from pathlib import Path

class Wordlist():
	"""Wordlist object.

	This is used by the 'erickapp' type of classifications to calculate document scores based upon
	words and their relevance for categories.

	It's also used by the Sping user application so it knows which words to show in the wordclouds
	for a certain category.

	Its most important asset is the df attribute. It's a pandas.DataFrame containing the columns
	`word`, `cat` and `score`. Each line shows how relevant (score) a word is for a category.

	"""
	cfg = ConfigParser().read("config.ini")
	findir = Path(cfg["dirs"]["finished"])
	wldir = cfg["dirs"]["wldir"]

	def __init__(self, df):
		"""Create the Wordlist object."""

		# Check if all necessary columns are present
		for col in "word cat score".split():
			if not col in list(df):
				raise WrongWordlistError("Column {} not found in the wordlistfile!".format(col))

		self.df = df


	@classmethod
	def from_file(cls, fn, **kwargs):
		"""Initialize a Wordlist object from a filename.

		If the extension is xlsx, read as an Excel file; else, read as CSV.
		Use the kwargs argument to pass arguments to the read functions of pandas.
		"""
		if fn.endswith(".xlsx"):
			# Read the Excel file
			df = pd.read_excel(fn, **kwargs)
		else:
			# Assume it's a csv file if it's not an Excel file
			df = pd.read_csv(fn, **kwargs)

		return cls(df)


	def create_wordlists(self, wldir=None, aid=None, use_cats=None, skip_cats=[]):
		"""Create a wordlist file for every category.

		Arguments:
			str | pathlib.Path `wldir`: directory to place wordlists in
			int | str `aid`: (if wldir is given, this is neglected): select wldir automatically
				based upon the audioset ID

		This is used by Sping's user application to show words in wordclouds per category.
		Scores are ignored in this function. There is a check for existing words though.
		For ngrams n>=2, spaces between words should be underscores according to Sping.
		"""
		if wldir is None:
			if aid is None:
				raise InsufficientInfoError("Provide at least aid or wldir")
			wldir = self.findir / str(self.aid) / self.wldir

		for cat in self.df.cat.unique():
			# This is built-in to prevent empty category cells
			if not cat:
				continue

			# Check if we really need to create this category
			if (use_cats is not None) and cat not in use_cats:
				continue

			# Check if we need to skip this category
			if cat in skip_cats:
				continue

			# Select the rows from the dataframe that belong to this category
			catdf = self.df[self.df.cat == cat]

			# Get the wordlist file
			wlfn = cat.capitalize() + ".txt"
			wlfile = wldir / wlfn
			wlfile.touch() # Create if it doesn't exist

			# Eliminate words that already exist in the wordlist file
			with wlfile.open() as wl_open:
				existing_words = set(wl_open.readlines())
			catdf = catdf[~catdf.word.isin(existing_words)]

			# Correct the words:
			# - lowercase
			# - underscores instead of spaces
			# - no trailing underscores
			corr_words = catdf.word.apply(lambda w: w.lower().replace(" ", "_").strip("_"))

			# Open the file and write the words
			with wlfile.open("a") as wl_open:
				for word in corr_words.unique():
					wl_open.write(word)

