# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) path specification mount point manager object.

The mount point manager allows to "mount" one path specification onto another.
This allows dfVFS to expose complex path specifications in a way closer to
the original system interpretation.

E.g. the path specification:
type=OS, location=/home/myuser/myimages/image.qcow2
type=QCOW
type=TSK_PARTITION, location=/p1
type=TSK, inode=128, location=/Users/MyUser/MyFile.txt

could be mounted as:
type=MOUNT, identifier=C
type=TSK, inode=128, location=/Users/MyUser/MyFile.txt

where the "C" mount point would be:
type=OS, location=/home/myuser/myimages/image.qcow2
type=QCOW
type=TSK_PARTITION, location=/p1
"""


class MountPointManager(object):
  """Class that implements the moint point manager."""

  _mount_points = {}

  @classmethod
  def DeregisterMountPoint(cls, mount_point):
    """Deregisters a path specification mount point.

    Args:
      mount_point: the mount point identifier.

    Raises:
      KeyError: if the corresponding mount point is not set.
    """
    if mount_point not in cls._mount_points:
      raise KeyError(
          u'Mount point: {0:s} not set.'.format(mount_point))

    del cls._mount_points[mount_point]

  @classmethod
  def GetMountPoint(cls, mount_point):
    """Retrieves the path specification of a mount point.

    Args:
      mount_point: the mount point identifier.

    Returns:
      The VFS path specification (instance of path.PathSpec) or None if
      the mount point does not exists.
    """
    return cls._mount_points.get(mount_point, None)

  @classmethod
  def RegisterMountPoint(cls, mount_point, path_spec):
    """Registers a path specification mount point.

    Args:
      mount_point: the mount point identifier.
      path_spec: the VFS path specification (instance of path.PathSpec).

    Raises:
      KeyError: if the corresponding mount point is already set.
    """
    if mount_point in cls._mount_points:
      raise KeyError(
          u'Mount point: {0:s} already set.'.format(mount_point))

    cls._mount_points[mount_point] = path_spec
