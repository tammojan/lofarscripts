#!/usr/bin/env python

# example basictreeview.py, stolen from http://pygtk.org/pygtk2tutorial/examples/basictreeview.py

import pygtk
pygtk.require('2.0')
import gtk
from lofar import parameterset as ps
import argparse
from collections import OrderedDict

def basekeys(allset):
    '''Returns ('b1','b2') from ['b1.bla','b1.bla2','b2.baea.fsda','b2.basde']'''
    ret = []
    for key in allset:
        ret+=[key.split('.')[0]]
    return list(OrderedDict.fromkeys(ret))

def el_index(element,llist):
    '''Return first index of element in llist, -1 for 'pipeline', or very large if element is not in llist'''
    if element=='pipeline':
        return -1
    try:
        idx=llist.index(element)
        return idx
    except ValueError:
        return 1000

class ParsetViewer:
    # close the window and quit
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def fill(self, p, treeiter = None):
        '''Fill treeview with contents of parset recursively'''
        if len(p)==0:
            return
        keys=basekeys(p.keys())
        if treeiter is None: 
            # Root level
            steps=p.getStringVector('pipeline.steps','[]')
            print steps
            if not self.showall:
              # Only show top-level elements that will get parsed
              keys=['pipeline']+steps
            # Order steps by their order in pipeline.steps
            keys=sorted(keys,key=lambda k:el_index(k, steps))
        for key in keys:
            piter=self.treestore.append(treeiter, [key,p.getString(key,'')])
            self.fill(p.makeSubset(key+'.'), piter)

    def __init__(self, parsetname, showall=False):
        # Store the showall-value
        self.showall=showall

        # Create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

        self.window.set_title(parsetname)

        self.window.set_size_request(400, 400)

        self.window.connect("delete_event", self.delete_event)

        self.scrolledwindow = gtk.ScrolledWindow()
        self.scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC) 

        # create a TreeStore with one string column to use as the model
        self.treestore = gtk.TreeStore(str,str)

        # add all data
        p=ps.parameterset(parsetname)
        self.fill(p)

        # create the TreeView using treestore
        self.treeview = gtk.TreeView(self.treestore)

        # create the TreeViewColumn to display the data
        self.keycolumn = gtk.TreeViewColumn('Key')
        self.valcolumn = gtk.TreeViewColumn('Value')

        # add keycolumn to treeview
        self.treeview.append_column(self.keycolumn)
        self.treeview.append_column(self.valcolumn)

        # create a CellRendererText to render the data
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable',True)

        # add the cell to the keycolumn and allow it to expand
        self.keycolumn.pack_start(self.cell, True)
        self.valcolumn.pack_start(self.cell, True)

        # set the cell "text" attribute to column 0 - retrieve text
        # from that column in treestore
        self.keycolumn.add_attribute(self.cell, 'text', 0)
        self.valcolumn.add_attribute(self.cell, 'text', 1)

        # make it searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.keycolumn.set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        # self.treeview.set_reorderable(True)

        self.scrolledwindow.add(self.treeview)

        self.window.add(self.scrolledwindow)

        self.window.show_all()

def main():
    gtk.main()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a LOFAR parameterset visually")
    parser.add_argument("parset", help="parset file")
    parser.add_argument("-a", "--all", help="Show all steps (even those not used", action='store_true')
    args=parser.parse_args()
    tvexample = ParsetViewer(args.parset, showall=args.all)
    main()

