# vim:encoding=utf-8:ts=2:sw=2:expandtab

from Project import *

@Expose
def Request(self):
  yield


  self.UI.Head('''
    <script type="text/paperscript" canvas="canvas" src="index.paper.js"></script>
    ''')

  self.UI.Body('''
    <strong>VectorGame</strong>
    <hr>

    
  
    ''')
  yield self.UI