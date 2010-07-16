import time, os, sys
import logging
import copy
import DataLoader
from xml.dom.minidom import parse
from lxml import etree

from DataLoader.readers.cansas_reader import Reader as CansasReader
from DataLoader.readers.cansas_reader import get_content
from sans.guiframe.utils import format_number
from sans.guiframe.dataFitting import Theory1D, Data1D
INVNODE_NAME = 'invariant'
CANSAS_NS = "cansas1d/1.0"
# default state
list = {'file': 'None',
        'compute_num':0,
        'state_num':0,
        'is_time_machine':False,
        'background_tcl':0.0,
        'scale_tcl':1.0,
        'contrast_tcl':1.0,
        'porod_constant_tcl':'',
        'npts_low_tcl':10,
        'npts_high_tcl':10,
        'power_high_tcl':4.0,
        'power_low_tcl': 4.0,
        'enable_high_cbox':False,
        'enable_low_cbox':False,
        'guinier': True,
        'power_law_high': False,
        'power_law_low': False,
        'fit_enable_high': False,
        'fit_enable_low': False,
        'fix_enable_high':True,
        'fix_enable_low':True,
        'volume_tcl':'',
        'volume_err_tcl':'',
        'surface_tcl':'',
        'surface_err_tcl':''}
# list of states: This list will be filled as panel init and the number of states increases
state_list = {}
bookmark_list = {}
# list of input parameters (will be filled up on panel init) used by __str__ 
input_list = {}   
# list of output parameters (order sensitive) used by __str__    
output_list = [["qstar_low",                  "Q* from low Q extrapolation [1/(cm*A)]"],
               ["qstar_low_err",             "dQ* from low Q extrapolation"],
               ["qstar_low_percent",  "Q* percent from low Q extrapolation"],
               ["qstar",                                     "Q* from data [1/(cm*A)]"],
               ["qstar_err",                                "dQ* from data"],
               ["qstar_percent",                     "Q* percent from data"],
               ["qstar_high",                "Q* from high Q extrapolation [1/(cm*A)]"],
               ["qstar_high_err",           "dQ* from high Q extrapolation"],
               ["qstar_high_percent", "Q* percent from low Q extrapolation"],
               ["qstar_total",                                   "total Q* [1/(cm*A)]"],
               ["qstar_total_err",                              "total dQ*"],
               ["volume",                                 "volume fraction"],
               ["volume_err",                       "volume fraction error"],
               ["surface",                               "specific surface"],
               ["surface_err",                     "specific surface error"]]

   

class InvariantState(object):
    """
    Class to hold the state information of the InversionControl panel.
    """
    def __init__(self):
        """
        Default values
        """
        # Input 
        self.file  = None
        self.data = Data1D(x=[], y=[], dx=None, dy=None)
        self.theory_lowQ =  Theory1D(x=[], y=[], dy=None)
        self.theory_highQ = Theory1D(x=[], y=[], dy=None)
        #self.is_time_machine = False
        self.saved_state = list
        self.state_list = state_list
        self.bookmark_list = bookmark_list
        self.input_list = input_list
        self.output_list = output_list
        
        self.compute_num = 0
        self.state_num = 0
        self.timestamp = None
        self.container = None
        
        
    def __str__(self):
        """
        Pretty print
            
        : return: string representing the state
        """
        # Input string
        compute_num = self.saved_state['compute_num']
        compute_state = self.state_list[str(compute_num)]
        my_time, date = self.timestamp
        file_name = self.file

        state_num = int(self.saved_state['state_num'])
        state = "\n[Invariant computation for %s: "% file_name
        state += "performed at %s on %s] \n"%(my_time, date)
        state += "State No.: %d \n"% state_num
        state += "\n=== Inputs ===\n"
        
        # text ctl general inputs ( excluding extrapolation text ctl)
        for key,value in self.input_list.iteritems(): 
            if value == '':
                continue
            key_split = key.split('_') 
            max_ind = len(key_split)-1
            if key_split[max_ind] == 'tcl': 
                name =""
                if key_split[1]== 'low' or key_split[1]== 'high':
                    continue
                for ind in range(0,max_ind):
                    name +=" %s"%key_split[ind]
                state += "%s:   %s\n"% (name.lstrip(" "),value)
                
        # other input parameters       
        extra_lo = compute_state['enable_low_cbox']
        if compute_state['enable_low_cbox']:
            if compute_state['guinier']:
                extra_lo = 'Guinier'
            else:
                extra_lo = 'Power law'
        extra_hi = compute_state['enable_high_cbox']
        if compute_state['enable_high_cbox']:
            extra_hi = 'Power law'
        state += "\nExtrapolation:  High=%s; Low=%s\n" %(extra_hi,extra_lo)   
        low_off = False
        high_off = False
        for key,value in self.input_list.iteritems(): 
            key_split = key.split('_') 
            max_ind = len(key_split)-1   
            if key_split[max_ind] == 'tcl': 
                name ="" 
                # check each buttons whether or not ON or OFF
                if key_split[1]== 'low' or key_split[1]== 'high':
                    if not compute_state['enable_low_cbox'] and key_split[max_ind-1] == 'low':
                        low_off = True
                        continue              
                    elif not compute_state['enable_high_cbox'] and key_split[max_ind-1]== 'high':
                        high_off = True
                        continue
                    elif extra_lo == 'Guinier' and key_split[0]== 'power' and key_split[max_ind-1]== 'low':
                        continue
                    for ind in range(0,max_ind):
                        name +=" %s"%key_split[ind]
                    name = name.lstrip(" ")
                    if name == "power low" :
                        if compute_state['fix_enable_low']:
                            name += ' (Fixed)'
                        else:
                            name += ' (Fitted)'
                    if name == "power high" :
                        if compute_state['fix_enable_high']:
                            name += ' (Fixed)'
                        else:
                            name += ' (Fitted)'
                    state += "%s:   %s\n"% (name,value)
        # Outputs
        state += "\n=== Outputs ==="
        for item in output_list:
            item_split = item[0].split('_') 
            # Exclude the extrapolation that turned off
            if len(item_split)>1:
                if low_off and item_split[1] == 'low': continue
                if high_off and item_split[1] == 'high': continue
            max_ind = len(item_split)-1
            value = None
            try:
                # Q* outputs
                exec "value = self.container.%s\n"% item[0]
            except:
                # other outputs than Q*
                name = item[0]+"_tcl"
                exec "value = self.saved_state['%s']"% name
                
            # Exclude the outputs w/''    
            if value == '': continue    
            
            # Error outputs
            if item_split[max_ind] == 'err':
                state += "+- %s "%format_number(value)
                
            # Percentage outputs
            elif item_split[max_ind] == 'percent':
                try:
                    value = float(value)*100
                except:
                    pass
                state += "(%s %s)"%(format_number(value),'%')
            # Outputs
            else:
                state += "\n%s:   %s "%(item[1],format_number(value,high=True))
        # Include warning msg
        state += "\n\nNote:\n" + self.container.warning_msg

        return state

    
    def clone_state(self):
        """
        deepcopy the state
        """
        return copy.deepcopy(self.saved_state)
    

    def toXML(self, file="inv_state.inv", doc=None, entry_node=None):
        """
        Writes the state of the InversionControl panel to file, as XML.
        
        Compatible with standalone writing, or appending to an
        already existing XML document. In that case, the XML document
        is required. An optional entry node in the XML document may also be given.
        
        : param file: file to write to
        : param doc: XML document object [optional]
        : param entry_node: XML node within the XML document at which we will append the data [optional]   
        """
        from xml.dom.minidom import getDOMImplementation
        import time
        timestamp = time.time()
        # Check whether we have to write a standalone XML file
        if doc is None:
            impl = getDOMImplementation()
        
            doc_type = impl.createDocumentType(INVNODE_NAME, "1.0", "1.0")     
        
            newdoc = impl.createDocument(None, INVNODE_NAME, doc_type)
            top_element = newdoc.documentElement
        else:
            # We are appending to an existing document
            newdoc = doc
            top_element = newdoc.createElement(INVNODE_NAME)
            if entry_node is None:
                newdoc.documentElement.appendChild(top_element)
            else:
                entry_node.appendChild(top_element)
            
        attr = newdoc.createAttribute("version")
        attr.nodeValue = '1.0'
        top_element.setAttributeNode(attr)
        
        # File name
        element = newdoc.createElement("filename")
        if self.file is not None:
            element.appendChild(newdoc.createTextNode(str(self.file)))
        else:
            element.appendChild(newdoc.createTextNode(str(file)))
        top_element.appendChild(element)
        
        element = newdoc.createElement("timestamp")
        element.appendChild(newdoc.createTextNode(time.ctime(timestamp)))
        attr = newdoc.createAttribute("epoch")
        attr.nodeValue = str(timestamp)
        element.setAttributeNode(attr)
        top_element.appendChild(element)
        
        # Current state
        state = newdoc.createElement("state")
        top_element.appendChild(state)
        
        for name,value in self.saved_state.iteritems():
            element = newdoc.createElement(str(name))
            element.appendChild(newdoc.createTextNode(str(value)))
            state.appendChild(element)
              
        # State history list
        history = newdoc.createElement("history")
        top_element.appendChild(history)
        
        for name, value in self.state_list.iteritems():
            history_element = newdoc.createElement('state_'+str(name))
            for state_name,state_value in value.iteritems():
                state_element = newdoc.createElement(str(state_name))
                state_element.appendChild(newdoc.createTextNode(str(state_value)))
                history_element.appendChild(state_element)
            #history_element.appendChild(state_list_element)
            history.appendChild(history_element)

        # Bookmarks  bookmark_list[self.bookmark_num] = [my_time,date,state,comp_state]
        bookmark = newdoc.createElement("bookmark")
        top_element.appendChild(bookmark)
        item_list = ['time','date','state','comp_state']
        for name, value_list in self.bookmark_list.iteritems():
            element = newdoc.createElement('mark_'+ str(name))
            time,date,state,comp_state = value_list
            time_element = newdoc.createElement('time')
            time_element.appendChild(newdoc.createTextNode(str(value_list[0])))
            date_element = newdoc.createElement('date')
            date_element.appendChild(newdoc.createTextNode(str(value_list[1])))
            state_list_element = newdoc.createElement('state')
            comp_state_list_element = newdoc.createElement('comp_state')
            for state_name,state_value in value_list[2].iteritems():
                state_element = newdoc.createElement(str(state_name))
                state_element.appendChild(newdoc.createTextNode(str(state_value)))
                state_list_element.appendChild(state_element)
            for comp_name,comp_value in value_list[3].iteritems():
                comp_element = newdoc.createElement(str(comp_name))
                comp_element.appendChild(newdoc.createTextNode(str(comp_value)))
                comp_state_list_element.appendChild(comp_element)
            element.appendChild(time_element)
            element.appendChild(date_element)
            element.appendChild(state_list_element)
            element.appendChild(comp_state_list_element)
            bookmark.appendChild(element)

        # Save the file
        if doc is None:
            fd = open('test000', 'w')
            fd.write(newdoc.toprettyxml())
            fd.close()
            return None
        else:
            return newdoc.toprettyxml()
        
    def fromXML(self, file=None, node=None):
        """
        Load invariant states from a file
            
        : param file: .inv file
        : param node: node of a XML document to read from       
        """
        if file is not None:
            raise RuntimeError, "InvariantSate no longer supports non-CanSAS format for invariant files"
        
        if node.get('version')\
            and node.get('version') == '1.0':

            # Get file name
            entry = get_content('ns:filename', node)
            if entry is not None:
                self.file = entry.text.strip()
            
            # Get time stamp
            entry = get_content('ns:timestamp', node)
            if entry is not None and entry.get('epoch'):
                try:
                    timestamp = (entry.get('epoch'))
                except:
                    logging.error("InvariantSate.fromXML: Could not read timestamp\n %s" % sys.exc_value)
            
            # Parse bookmarks
            entry_bookmark = get_content('ns:bookmark', node)

            for ind in range(1,len(entry_bookmark)+1):
                temp_state = {}
                temp_bookmark = {}
                entry = get_content('ns:mark_%s' % ind, entry_bookmark) 
                                
                if entry is not None:
                    time = get_content('ns:time', entry )
                    val_time = str(time.text.strip())
                    date = get_content('ns:date', entry )
                    val_date = str(date.text.strip())
                    state_entry = get_content('ns:state', entry )
                    for item in list:

                        input_field = get_content('ns:%s' % item, state_entry )
                        val = str(input_field.text.strip())

                        if input_field is not None:
                            try:
                                exec "temp_state['%s'] = %s"% (item,val)      
                            except:
                                exec "temp_state['%s'] = '%s'"% (item,val)

                            
                    comp_entry = get_content('ns:comp_state', entry )
                    
                    for item in list:
                        input_field = get_content('ns:%s' % item, comp_entry )
                        val = str(input_field.text.strip())
                        if input_field is not None:
                            try:
                                exec "temp_bookmark['%s'] = %s"% (item,val)      
                            except:
                                exec "temp_bookmark['%s'] = '%s'"% (item,val)
                    try:
                        exec "self.bookmark_list[%s] = [val_time,val_date,temp_state,temp_bookmark]"% ind

                    except:
                        raise "missing components of bookmarks..."
    
            # Parse histories
            entry_history = get_content('ns:history', node)

            for ind in range(0,len(entry_history)):
                temp_state = {}
                entry = get_content('ns:state_%s' % ind, entry_history) 

                if entry is not None:
                    for item in list:
                        input_field = get_content('ns:%s' % item, entry )
                        val = str(input_field.text.strip())

                        if input_field is not None:
                            try:
                                exec "temp_state['%s'] = %s"% (item,val)         
                            except:
                                exec "temp_state['%s'] = '%s'"% (item,val)
                            finally:
                                exec "self.state_list['%s'] = temp_state"% ind 
            
            # Parse current state (ie, saved_state)
            entry = get_content('ns:state', node)           
            if entry is not None:
                for item in list:
                    input_field = get_content('ns:%s' % item, entry)
                    val = str(input_field.text.strip())
                    if input_field is not None:
                        self.set_saved_state(name=item, value=val)


            
    def set_saved_state(self, name, value):
        """
        Set the state list 
                    
        : param name: name of the state component
        : param value: value of the state component
        """
        rb_list = [['power_law_low','guinier'],['fit_enable_low','fix_enable_low'],['fit_enable_high','fix_enable_high']]

        try:
            if value == None or value.lstrip().rstrip() =='':
                exec "self.%s = '%s'" % (name, value)
                exec "self.saved_state['%s'] = '%s'" %  (name, value)
            else:
                exec 'self.%s = %s' % (name, value)
                exec "self.saved_state['%s'] = %s" %  (name, value)

            
            # set the count part of radio button clicked False for the saved_state
            for title,content in rb_list:
                if name ==  title:
                    name = content 
                    value = False     
                elif name == content:
                    name = title
                    value = False 
            exec "self.saved_state['%s'] = '%s'" %  (name, value)     
            self.state_num = self.saved_state['state_num']
        except:           
            pass



class Reader(CansasReader):
    """
    Class to load a .inv invariant file
    """
    ## File type
    type_name = "Invariant"
    
    ## Wildcards
    type = ["Invariant file (*.inv)|*.inv"]
    ## List of allowed extensions
    ext=['.inv', '.INV']  
    
    def __init__(self, call_back, cansas=True):
        """
        Initialize the call-back method to be called
        after we load a file
        
        : param call_back: call-back method
        : param cansas:  True = files will be written/read in CanSAS format
                        False = write CanSAS format  
        """
        ## Call back method to be executed after a file is read
        self.call_back = call_back
        ## CanSAS format flag
        self.cansas = cansas

    def read(self, path):
        """ 
        Load a new invariant state from file
        
        : param path: file path
        : return: None
        """
        if self.cansas==True:
            return self._read_cansas(path)
        else:
            return self._read_standalone(path)
        
    def _read_standalone(self, path):
        """ 
        Load a new invariant state from file.
        The invariant node is assumed to be the top element.
        
        : param path: file path
        : return: None
        """
        # Read the new state from file
        state = InvariantState()

        state.fromXML(file=path)
        
        # Call back to post the new state
        self.call_back(state)
        return None
    
    def _parse_state(self, entry):
        """
        Read an invariant result from an XML node
        
        : param entry: XML node to read from 
        : return: InvariantState object
        """
        # Create an empty state
        state = InvariantState()

        # Locate the invariant node
        try:
            nodes = entry.xpath('ns:%s' % INVNODE_NAME, namespaces={'ns': CANSAS_NS})
            state.fromXML(node=nodes[0])
        except:
            logging.info("XML document does not contain invariant information.\n %s" % sys.exc_value)  
        return state
    
    def _read_cansas(self, path):
        """ 
        Load data and invariant information from a CanSAS XML file.
        
        : param path: file path
        : return: Data1D object if a single SASentry was found, 
                    or a list of Data1D objects if multiple entries were found,
                    or None of nothing was found
        : raise RuntimeError: when the file can't be opened
        : raise ValueError: when the length of the data vectors are inconsistent
        """
        output = []
        
        if os.path.isfile(path):
            basename  = os.path.basename(path)
            root, extension = os.path.splitext(basename)
            
            if  extension.lower() in self.ext or \
                extension.lower() == '.xml':
                tree = etree.parse(path, parser=etree.ETCompatXMLParser())
       
                # Check the format version number
                # Specifying the namespace will take care of the file format version 
                root = tree.getroot()
                
                entry_list = root.xpath('/ns:SASroot/ns:SASentry', namespaces={'ns': CANSAS_NS})
                
                for entry in entry_list:
                    
                    sas_entry = self._parse_entry(entry)
                    invstate = self._parse_state(entry)
                    sas_entry.meta_data['invstate'] = invstate

                    sas_entry.filename = invstate.file
                    output.append(sas_entry)
                
        else:
            raise RuntimeError, "%s is not a file" % path

        # Return output consistent with the loader's api
        if len(output)==0:
            return None
        elif len(output)==1:
            # Call back to post the new state

            self.call_back(state=output[0].meta_data['invstate'], datainfo = output[0])
            return output[0]
        else:
            return output                
    
    
    def write(self, filename, datainfo=None, invstate=None):
        """
        Write the content of a Data1D as a CanSAS XML file
        
        : param filename: name of the file to write
        : param datainfo: Data1D object
        : param invstate: InvariantState object
        """

        # Sanity check
        if self.cansas == True:
            if datainfo is None:
                datainfo = DataLoader.data_info.Data1D(x=[], y=[])    
            elif not issubclass(datainfo.__class__, DataLoader.data_info.Data1D):
                raise RuntimeError, "The cansas writer expects a Data1D instance: %s" % str(datainfo.__class__.__name__)
        
            # Create basic XML document
            doc, sasentry = self._to_xml_doc(datainfo)
        
            # Add the invariant information to the XML document
            if invstate is not None:
                invstate.toXML(doc=doc, entry_node=sasentry)
        
            # Write the XML document
            fd = open(filename, 'w')
            fd.write(doc.toprettyxml())
            fd.close()
        else:
            invstate.toXML(file=filename)
        
    
    