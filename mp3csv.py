import os
import eyed3
import csv
from operator import itemgetter

def scan_tree (startpath, d):
    for root, dirs, files in os.walk(startpath):
        for f in files:
            path = os.path.join(root, f)
            tags = eyed3.load(path)
            if tags is not None:
                tt = tags.tag
                a = {}
                a['track'] = ''
                track = tt.track_num[0]
                if track is None:
                    a['track'] = ''
                    a['track_sort'] = -1
                else:
                    a['track'] = str(track)
                    a['track_sort'] = track
                artistes = getattr(tt, 'artist', getattr(tt, 'album_artist', ''))
                if artistes is None:
                    artistes = ''
                a['artists'] = artistes
                a['title'] = tt.title if tt.title is not None else ''
                a['album'] = tt.album if tt.album is not None else ''
                a['path'] = path

                artist_list = artistes.split(' / ')
                for al1 in artist_list:
                    al = a.copy()
                    al['artist'] = al1
                    #print(al)
                    d.append(al)
            else:
                print("**", path)

def main():
    d = []
    scan_tree ("/media/wegscd/727A44047A43C397/Users/dwegs/Music/mp3", d)
    for d1 in d:
        print(d1)
        xx = itemgetter('artist', 'album', 'track_sort')(d1)
        if None in xx:
            raise Exception()
    d.sort(key=itemgetter('artist', 'album', 'track_sort'))
    for d1 in d:
        print(d1)
    with open('all.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, ['artist', 'album', 'title', 'track', 'artists'], extrasaction='ignore')
        dw.writeheader()
        for d1 in d:
            dw.writerow(d1)
    with open('all_with_paths.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, ['artist', 'album', 'title', 'track', 'artists', 'path'], extrasaction='ignore')
        dw.writeheader()
        for d1 in d:
            dw.writerow(d1)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
