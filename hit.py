

class Hit(object):
	def __init__(self, word, t0=None, tx=None, conf=None, spk=None):
		self.word = word
		self.t0 = t0
		self.tx = tx
		self.conf = conf
		self.spk = spk

	def __repr__(self):
		return "{}({})".format(self.__class__.__name__, self.word)

	@classmethod
	def from_namedtuple(cls, tup):
		"""Create hit from a namedtuple using a pandas.core.frame.Pandas object.

		Very handy for bulk creating hits from a pandas.DataFrame (use df.itertuples() for this).
		"""
		return cls(**tup._asdict())
