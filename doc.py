import pandas as pd

from pathlib import Path

from hit import Hit

class Document(object):
	def __init__(self, loc):
		"""Initialize a Document object by a location."""
		self.path = Path(self.loc)
		self.hits = []


	@classmethod
	def from_text(self, txt):
		"""Initialize a Document object by a text (useful for texts in Excel files, for example)."""
		self.path = None
		self.hits = read_hits(txt=txt)


	@property
	def barefn(self):
		"""str: The filename, without path or extension"""
		return self.path.stem


	@property
	def origloc(self):
		"""str: The full filepath to self.path, as a string."""
		if path is None:
			raise ValueError("This {cls} has no location; instantiate it using {cls}().". \
				format(cls=self.__class__.__name__))
		return self.path.as_posix()


	def classify(self, method="erickapp", inplace=False, **kwargs):
		"""Classify the document.

		Arguments:
			str `method`: 'erickapp' | 'sklearn'
				- 'erickapp': Calculate a score for each given category. Categories are defined by
					words and their relevance for the categories. For this, a CatsRel object is
					used that should be passed using kwargs; this should have a pandas.DataFrame
					`df` attribute that contains a DataFrame with these columns:
						- word: the words (or ngrams) used to classify
						- cat: the category for the word
						- score: the relevance of the word for the category
					A score `s` for cat `c` is calculated as follows:
						s = sum_w(r_w * c_w) * n / d
					This means: sum for all words that occur in the document AND have a score in
						the catsrel file, and correct by some factors.
						- r_w is the score for each word in that category
						- c_w is the confidence of the word: ~P(correct recognition result)
						- n is the number of *unique* words in the document
						- d is a correction factor, can be passed in kwargs["corr"]:
							- "dur" (default): the duration of the file in seconds
							- "logdur": the 10log of the duration in seconds
							- "nwd": the number of words in the file
							- "no": no correction factor
				- 'sklearn': Calculate a probability for each class (in the order of training).
					You should pass kwargs["clf"]: an sklearn classifier object with a
					.predict_proba() method.
			bool `inplace`: Whether to save classifications in self.classifications

		Returns:
			Dependent on method:
				'erickapp' -- dict: with {category: score} mappings
				'sklearn' -- np.array: with probabilities (0-1) for each category
		"""
		if not self.hits:
			hits = self.read_hits()

		clfs = {}

		if inplace:
			self.classifications = clfs

		return clfs

	def read_hits(self, txt=None, path=None, format=None, using=None, inplace=False, **kwargs):
		"""Create a list of Hit objects from a file or a given text.

		Arguments:
			- str `txt`: the text to read hits from (if it's given, format="txt" and using="txt").
			- pathlib.Path `path`: the file to read hits from.
			- str `format`: (if `path` is given) how to read hits; one of the following:
				- txt: file contains just the words
				- csv: file contains columns with words (reads from self.path by default but
					you can define path to override that)
					Define column names as a dict in kwargs["colnames"]. Available keys are
						"word", "t0", "tx", "conf" (weight) and "spk" (speaker), and default values
						are the same as the keys.
					You can also define kwargs for pandas.read_csv in kwargs.
				- nuance: lattice file from Nuance Transcription Engine
				- google: lattice file from Google Speech-to-Text
				- spraak: lattice file from SPRaak
			- str `using`: where to read the hits from; one of the following:
				- file: open a file and read the contents (also, set self.txt)
				- txt: use self.txt
				- None: use self.file if it exists, else use self.txt
			- bool `inplace`: save hits in self.hits if True, else just return them
		"""

		if txt is not None:
			pass
		elif self.path is None or using == "txt":
			txt = self.txt
		elif using == "file":
			with self.path.open() as lines:
				txt = lines.read()
		else:
			raise ValueError("Argument `using` should be 'file', 'txt' or None.")

		if format == "txt":
			hits = []
			for word in txt.split():
				hit = Hit(word)
				hits.append(hit)
		elif format == "csv":
			path = self.path or Path(path)
			docdf = pandas.read_csv(path.as_posix(), **kwargs). \
				rename(columns=kwargs.get("colnames", {}))
			for row in docdf.itertuples():
				hit = Hit.from_namedtuple(row)
				hits.append(hit)
		else:
			raise NotImplementedError("Reading hits from {} doesn't work yet.".format(format))

		if inplace:
			self.hits = hits

		return hits
