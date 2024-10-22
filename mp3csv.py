import os
import eyed3
import csv
import datetime
import fnmatch
import sqlite3
from operator import itemgetter


def scan_tree(startpath, d_all, d_albums):
    for root, dirs, files in os.walk(startpath):
        for f in files:
            if fnmatch.fnmatch(f, "*.mp3"):
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
                    album = a['album'] = tt.album if tt.album is not None else ''
                    a['path'] = path

                    mtime = os.path.getmtime(path)
                    a['mtime'] = str(datetime.datetime.fromtimestamp(mtime).isoformat())

                    artist_list = artistes.split(' / ')
                    for al1 in artist_list:
                        al = a.copy()
                        al['artist'] = al1
                        # print(al)
                        d_all.append(al)

                        if album != '' and album.lower() != 'youtube':
                            a_key = (al['artist'], al['album'])
                            d_albums[a_key] = al
                else:
                    print("**", path)


def main():
    d = []
    d_albums = {}
    scan_tree("/media/wegscd/948E51A08E517BA4/Users/dwegs/Music/mp3", d, d_albums)
    for d1 in d:
        print(d1)
        xx = itemgetter('artist', 'album', 'track_sort')(d1)
        if None in xx:
            raise Exception()
    d.sort(key=itemgetter('artist', 'album', 'track_sort'))
    for d1 in d:
        print(d1)
    with open('all.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, ['artist', 'album', 'title', 'track', 'mtime', 'artists'], extrasaction='ignore')
        dw.writeheader()
        for d1 in d:
            dw.writerow(d1)
    with open('all_with_paths.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, ['artist', 'album', 'title', 'track', 'artists', 'path'], extrasaction='ignore')
        dw.writeheader()
        for d1 in d:
            dw.writerow(d1)

    d_albums = list(d_albums.values())
    d_albums.sort(key=itemgetter('artist', 'album'))
    with open('albums.csv', 'w', newline='') as f:
        dw = csv.DictWriter(f, ['artist', 'album', 'artists'], extrasaction='ignore')
        dw.writeheader()
        for d1 in d_albums:
            dw.writerow(d1)

    print("Creating db")
    os.remove('new.db')
    with sqlite3.connect('new.db') as conn:
        cur = conn.cursor()
        cur.executescript('''
CREATE TABLE IF NOT EXISTS "Tracks" (
	"Artist"	TEXT COLLATE NOCASE,
	"Album"	TEXT,
	"Title"	TEXT,
	"Track"	INTEGER,
	"Artists"	TEXT
);

CREATE INDEX "I_AAT" ON "Tracks" (
	"Artist"	ASC,
	"Album"	ASC,
	"Title"	ASC
);
''')

        for d1 in d:
            print(d1)
            cur.execute("insert into tracks (Artist, Album, Title, Track, Artists) VALUES (:artist, :album, :title, :track_sort, :artists)", d1)
        conn.commit()

        tracks = {}
        for d1 in d:
            tracks[d1['path']] = d1
        tracks = list(tracks.values())

        tracks.sort(key=itemgetter('mtime'), reverse=True)
        with open('mtime.m3u', 'w') as f:
            for t1 in tracks:
                print("#" + t1['mtime'], file=f)
                print(t1['path'], file=f)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
