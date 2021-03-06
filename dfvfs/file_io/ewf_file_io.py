# -*- coding: utf-8 -*-
"""The EWF image file-like object."""

import pyewf

from dfvfs import dependencies
from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.lib import ewf
from dfvfs.resolver import resolver


dependencies.CheckModuleVersion(u'pyewf')


class EwfFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyewf."""

  def __init__(self, resolver_context, file_object=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_object: optional file-like object. The default is None.

    Raises:
      ValueError: when file_object is set.
    """
    if file_object:
      raise ValueError(u'File object value set.')

    super(EwfFile, self).__init__(resolver_context)
    self._file_objects = []

  def _Close(self):
    """Closes the file-like object.

       If the file-like object was passed in the init function
       the data range file-like object does not control the file-like object
       and should not actually close it.

    Raises:
      IOError: if the close failed.
    """
    # pylint: disable=protected-access
    super(EwfFile, self)._Close()

    for file_object in self._file_objects:
      file_object.close()

    self._file_objects = []

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object or None.

    Raises:
      PathSpecError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    parent_path_spec = path_spec.parent

    file_system = resolver.Resolver.OpenFileSystem(
        parent_path_spec, resolver_context=self._resolver_context)

    # Note that we cannot use pyewf's glob function since it does not
    # handle the file system abstraction dfvfs provides.
    segment_file_path_specs = ewf.EwfGlobPathSpec(file_system, path_spec)
    if not segment_file_path_specs:
      return

    if parent_path_spec.IsSystemLevel():
      # Typically the file-like object cache should have room for 127 items.
      self._resolver_context.SetMaximumNumberOfFileObjects(
          len(segment_file_path_specs) + 127)

    for segment_file_path_spec in segment_file_path_specs:
      file_object = resolver.Resolver.OpenFileObject(
          segment_file_path_spec, resolver_context=self._resolver_context)
      self._file_objects.append(file_object)

    ewf_handle = pyewf.handle()
    ewf_handle.open_file_objects(self._file_objects)
    return ewf_handle

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._file_object.get_media_size()
