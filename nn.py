from math import tanh
import sqlite3 as sqlite  # use the bundled mysq   l

class searchnet:
  def __init__(self, dbname):
    self.con = sqlite.connect(dbname)

  def __del__(self):
    self.con.close()

  def maketables(self):
    self.con.execute('create table hiddennode(create_key)')
    self.con.execute('create table wordhidden(fromid, toid, strength)')
    self.con.execute('create table hiddenurl(fromid, toid, strength)')
    self.con.commit()

  def tablename(self, layer):
    return ['wordhidden', 'hiddenurl'][layer]

  def getstrength(self, fromid, toid, layer):
    """Gets a connection strength from the db, returns a default value if
    no value is found in the db."""
    table = self.tablename(layer)
    res = self.con.execute('select strength from %s where fromid = %d' %
        (table, fromid, toid)).fetchone()
    if res == None:
      return [-0.2, 0][layer]
    return res[0]

  def setstrength(self, fromid, toid, layer, strength):
    table = self.tablename(layer)
    res = self.con.execute(
        'select rowid from %s where fromid = %s and toid = %s'
        % (table, fromid, toid)).fetchone()
    if res == None:
      self.con.execute('insert into %s (fromid, toid, strength) ' % table
          + 'values (%d, %d, %f)' % (fromid, toid, strength))
    else:
      self.con.execute('update %s set strength %s where rowid = %d'
          % (table, strength, res[0]))

  def generatehiddennode(self, wordids, urls):
    """Checks if a given combination of words was already learned. If not,
    connects the words to a new hidden node and this hidden node to urls.
    
    This means that the set of urls for a given set of words can not be
    changed once it has been set."""
    if len(wordids) > 3: return None

    # Did we already create a node for this set of words?
    createkey = '_'.join(sorted(map(str, wordids)))
    res = self.con.execute(
        'select rowid from hiddennode where create_key = "%s"'
        % createkey).fetchone()

    # If not, do so now
    if res == None:
      cur = self.con.execute('insert into hiddennode (create_key) values ("%s")'
          % createkey)
      hiddenid = cur.lastrowid

      # create default values that indicate the connection between wordids and
      # urls
      for wordid in wordids:
        self.setstrength(wordid, hiddenid, 0, 1.0/len(wordids))
      for urlid in urls:
        self.setstrength(hiddenid, urlid, 1, 0.1)
      self.con.commit()


if __name__ == '__main__':
  net = searchnet('nn.db')
  net.maketables()

  words = [101, 102]
  urls = [201, 202, 203]
  net.generatehiddennode(words, urls)

  for c in net.con.execute('select * from hiddennode'): print c
  for c in net.con.execute('select * from wordhidden'): print c
  for c in net.con.execute('select * from hiddenurl'): print c