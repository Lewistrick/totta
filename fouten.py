class TottaError(Exception):
	"""Base class for all custom errors."""
	pass

class ConversionError(TottaError):
	pass

class ExtensionError(TottaError):
	pass