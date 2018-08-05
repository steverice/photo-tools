import appex
import photos
import dialogs
from PIL import Image
from collections import defaultdict

#import re


def main():
  if not appex.is_running_extension():

    assets = choose_assets()
    if assets is None: return

    process_assets(assets)
  else:
    images = appex.get_attachments()
    print(images)
    #print(re.findall('[a-fA-F0-9]+\-[a-FA-F0-9]+', image))


def choose_assets():
  search = dialogs.input_alert('What is your album called?')

  albums = photos.get_albums()
  albums = list(
    sorted(
      list([a for a in albums if len(a.assets) > 0 and search in a.title]),
      key=lambda a: a.end_date or '1970-01-01',
      reverse=True))

  if len(albums) == 0:
    dialogs.hud_alert('No album found!')
    return None

  album_names = [
    {
      'id': a.local_id,
      'index': i,
      'title': "{0} ({1})".format(a.title, a.end_date),
      #'image': a.assets[0].get_image(),
      'accessory_type': 'checkmark'
    } for (i, a) in enumerate(albums)
  ]
  album = dialogs.list_dialog('Choose Album', album_names)

  if album is None: return None

  album_index = album['index']
  assets = photos.pick_asset(albums[album_index], 'Choose Photos', True)

  return assets


def process_assets(assets):
  to_delete = []

  groups = defaultdict(list)
  for asset in assets:
    groups[asset.creation_date].append(asset)

  for tuple in groups.values():
    if len(tuple) < 2: continue
    j = tuple[0]
    k = tuple[1]
    new_photo = None
    old_photo = None
    print(j.location)
    print(k.location)
    if j.location is None and k.location is not None:
      new_photo = j
      old_photo = k
    elif k.location is None and j.location is not None:
      new_photo = k
      old_photo = j
    if new_photo is not None and old_photo is not None:
      print(new_photo)
      if new_photo.can_edit_properties:
        new_photo.location = old_photo.location
        print(new_photo.location)
        if new_photo.location and old_photo.can_delete:
          to_delete.append(old_photo)

  if len(to_delete) > 0:
    photos.batch_delete(to_delete)


if __name__ == '__main__':
  main()

