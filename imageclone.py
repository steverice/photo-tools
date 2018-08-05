import appex
import photos
import dialogs
import ui
from PIL import Image
from collections import defaultdict, namedtuple

#import re


def main():
  if not appex.is_running_extension():

    assets = choose_assets()
    if assets is None: return

    assets = process_assets(assets)

    if len(assets.deletable) > 0:
      photos.batch_delete(assets.deletable)

    dialogs.hud_alert("{0} photos updated".format(len(assets.new)))
  else:
    images = appex.get_attachments()
    print(images)
    #print(re.findall('[a-fA-F0-9]+\-[a-FA-F0-9]+', image))


def choose_assets():
  search = dialogs.input_alert('What is your album called?')

  albums = photos.get_albums()
  albums = list([a for a in albums if search in a.title])
  albums = list([a for a in albums if get_album_ends(a)[0] is not None])

  if len(albums) == 0:
    dialogs.hud_alert('No album found!', icon='error')
    return None

  album_names = [
    {
      'id': a.local_id,
      'index': i,
      'title': "{0} ({1})".format(a.title, get_album_dates(a)[0].strftime('%b %d, %Y')),
      #'image': get_asset_thumb(get_album_ends(a)[0]),
      'accessory_type': 'checkmark'
    } for (i, a) in enumerate(albums)
  ]
  album = dialogs.list_dialog('Choose Album', album_names)

  if album is None: return None

  album_index = album['index']
  assets = photos.pick_asset(albums[album_index], 'Choose Photos', True)

  return assets


def process_assets(assets):
  ProcessedAssets = namedtuple('ProcessedAssets', ['new', 'deletable'])
  processed_assets = ProcessedAssets(new=[], deletable=[])

  groups = defaultdict(list)
  for asset in assets:
    groups[asset.creation_date].append(asset)

  for tuple in groups.values():
    if len(tuple) < 2: continue
    j = tuple[0]
    k = tuple[1]
    new_photo = None
    old_photo = None
    if j.location is None and k.location is not None:
      new_photo = j
      old_photo = k
    elif k.location is None and j.location is not None:
      new_photo = k
      old_photo = j
    if new_photo is not None and old_photo is not None:
      if new_photo.can_edit_properties:
        new_photo.location = old_photo.location
        new_photo.favorite = old_photo.favorite
        processed_assets.new.append(new_photo)
        if old_photo.can_delete:
          processed_assets.deletable.append(old_photo)

  return processed_assets


def get_album_ends(album: photos.AssetCollection):
  assets = album.assets
  if len(assets) == 0:
    return (None, None)
  else:
    return (assets[0], assets[-1])


def get_album_dates(album: photos.AssetCollection):
  # https://forum.omz-software.com/topic/3235/photos-module-album-start-date-end-date/2
  ends = get_album_ends(album)
  return (getattr(ends[0], 'creation_date'), getattr(ends[-1], 'creation_date'))


def get_asset_thumb(asset: photos.Asset):
  # from https://forum.omz-software.com/topic/4599/heic-photo-file-issues-in-ios11/3
  pngdata = ui.Image.from_data(asset.get_image_data().getvalue()).to_png()
  pil_image = Image.open(io.BytesIO(pngdata))
  return pil_image


if __name__ == '__main__':
  main()

