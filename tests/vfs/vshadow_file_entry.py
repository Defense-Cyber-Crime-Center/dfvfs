#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the file entry implementation using the pyvshadow."""

import os
import unittest

from dfvfs.path import os_path_spec
from dfvfs.path import qcow_path_spec
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import vshadow_file_entry
from dfvfs.vfs import vshadow_file_system


class VShadowFileEntryTest(unittest.TestCase):
  """The unit test for the VSS file entry object."""

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()
    test_file = os.path.join(u'test_data', u'vsstest.qcow2')
    path_spec = os_path_spec.OSPathSpec(location=test_file)
    self._qcow_path_spec = qcow_path_spec.QcowPathSpec(parent=path_spec)
    self._vshadow_path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)

    self._file_system = vshadow_file_system.VShadowFileSystem(
        self._resolver_context)
    self._file_system.Open(path_spec=self._vshadow_path_spec)

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._file_system.Close()

  # qcowmount test_data/vsstest.qcow2 fuse/
  # vshadowinfo fuse/qcow1
  #
  # Volume Shadow Snapshot information:
  #   Number of stores:	2
  #
  # Store: 1
  #   ...
  #   Identifier		: 600f0b69-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 0a4e3901-6abb-48fc-95c2-6ab9e38e9e71
  #   Creation time		: Dec 03, 2013 06:35:09.736378700 UTC
  #   Shadow copy ID		: 4e3c03c2-7bc6-4288-ad96-c1eac1a55f71
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009
  #
  # Store: 2
  #   Identifier		: 600f0b6d-5bdf-11e3-9d6c-005056c00008
  #   Shadow copy set ID	: 8438a0ee-0f06-443b-ac0c-2905647ca5d6
  #   Creation time		: Dec 03, 2013 06:37:48.919058300 UTC
  #   Shadow copy ID		: 18f1ac6e-959d-436f-bdcc-e797a729e290
  #   Volume size		: 1073741824 bytes
  #   Attribute flags		: 0x00420009

  def testIntialize(self):
    """Test the initialize functionality."""
    file_entry = vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self._file_system, self._vshadow_path_spec)

    self.assertNotEqual(file_entry, None)

  def testGetParentFileEntry(self):
    """Test the get parent file entry functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    parent_file_entry = file_entry.GetParentFileEntry()

    self.assertEqual(parent_file_entry, None)

  def testGetStat(self):
    """Test the get stat functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    stat_object = file_entry.GetStat()

    self.assertNotEqual(stat_object, None)
    self.assertEqual(stat_object.type, stat_object.TYPE_FILE)

  def testIsFunctions(self):
    """Test the Is? functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        store_index=1, parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertFalse(file_entry.IsRoot())
    self.assertFalse(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertFalse(file_entry.IsDirectory())
    self.assertTrue(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertTrue(file_entry.IsRoot())
    self.assertTrue(file_entry.IsVirtual())
    self.assertTrue(file_entry.IsAllocated())

    self.assertFalse(file_entry.IsDevice())
    self.assertTrue(file_entry.IsDirectory())
    self.assertFalse(file_entry.IsFile())
    self.assertFalse(file_entry.IsLink())
    self.assertFalse(file_entry.IsPipe())
    self.assertFalse(file_entry.IsSocket())

  def testSubFileEntries(self):
    """Test the sub file entries iteration functionality."""
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=u'/', parent=self._qcow_path_spec)
    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)

    self.assertNotEqual(file_entry, None)

    self.assertEqual(file_entry.number_of_sub_file_entries, 2)

    expected_sub_file_entry_names = [u'vss1', u'vss2']

    sub_file_entry_names = []
    for sub_file_entry in file_entry.sub_file_entries:
      sub_file_entry_names.append(sub_file_entry.name)

    self.assertEqual(
        len(sub_file_entry_names), len(expected_sub_file_entry_names))
    self.assertEqual(
        sorted(sub_file_entry_names), sorted(expected_sub_file_entry_names))


if __name__ == '__main__':
  unittest.main()
