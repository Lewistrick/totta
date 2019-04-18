from configparser import ConfigParser

from doc import Document
from fouten import ConversionError, ExtensionError

class AudioDocument(Document):
	"""An audio document, e.g. a conversation.

	Subclass of Document (that contains a lot of handy methods generic to all document types).
	"""
	cfg = ConfigParser().read("config.ini")
	ffmpeg = cfg["dependencies"]["ffmpeg"]
	lame = cfg["dependencies"]["lame"]


	def __init__(self, loc):
		"""Create the AudioDocument instance.

		The `loc` attribute should in most cases be the location of the *original* audio file
		that the client transferred. This is because of the directory structure for clients:
		/data/processing/[CUSTOMER_ID]/[AUDIOSET_ID] is the directory that contains all calls
		in a given audioset for a given customer.

		"""
		super().__init__(self, loc)


	@property
	def wavloc(self):
		"""str: The filepath to the wave file, as a string.

		If the file doesn't exist, try to convert it
		"""
		if hasattr(self, "wavpath"):
			return self.wavpath.as_posix()

		self.wavpath = self.path.parent.parent / "wav" / self.stem + ".wav"
		if not self.wavpath.exists():
			raise FileNotFoundError("")
		return self.wavpath.as_posix()


	def convert(self, ext, src=None, tgt=None, overwrite=False):
		"""Convert an audiofile to a given extension `ext`.

		Arguments:
			str `ext`: the extension to convert to. Either 'wav' (ffmpeg is used) or 'mp3' (lame).
			str `src`: the source location to convert from. Default: self.origloc.
			str `tgt`: the target location of the new file. Default: ../<EXT>/<STEM>.<EXT>
				where EXT = the given extension and STEM = the filename without
			bool `overwrite`: whether to overwrite an existing file

		Returns:
			Path:
		"""

		if src is None:
			src = self.origloc # property of Document

		if tgt is None:
			tgtdir = self.path.parent.parent / ext
			tgtdir.mkdir(parents=True, exist_ok=True) # create the dir it if it doesn't exist
			tgtpath = tgtdir / "{}.{}".format(self.stem, ext)
			tgt = str(tgtpath)

		if ext == "wav":
			command = [
				self.ffmpeg,
				"-loglevel", "panic",
				"-i", src,
				"-ar", "8000",
				"-ab", "16K",
				"-ac", "1",
				tgt, "-y"
			]
			self.wavloc = tgt
		elif ext == "mp3":
			command = [
				self.lame,
				"-q", "9",
				"-b", "16",
				src, tgt,
				"--silent"
			]
			self.mp3loc = tgt
		else:
			raise ExtensionError("Kan niet converteren naar extensie: {}".format(ext))

		errdir = self.path.parent.parent / "errors"
		errdir.mkdir(parents=True, exist_ok=True) # create the dir it if it doesn't exist
		errfile = errdir / self.barefn
		errfile.touch() # create the file if it doesn't exist

		with errfile.open("a") as errstream: # write errors to error file
			try:
				subprocess.check_call(command, stderr=errfile)
			except CalledProcessError as err:
				raise ConversionError("Foutmelding bij conversie naar {}: {}".format(ext, err))

