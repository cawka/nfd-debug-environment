import gdb
import boost
import pyndn

printer_gen = boost.utils.Printer_Gen('ndn')

# This function registers the top-level Printer generator with gdb.
# This should be called from .gdbinit.
def register_ndn_printers(obj):
    "Register printer generator with objfile obj."

    global printer_gen

    boost.utils.message('registering top-level printers:' +
            ' (name="' + printer_gen.name + '" id=' + str(id(printer_gen)) + ')' +
            ' with objfile=' + str(obj))
    gdb.printing.register_pretty_printer(obj, printer_gen, replace=True)

# Register individual Printer with the top-level Printer generator.
def _register_printer(Printer):
    "Registers a Printer"
    printer_gen.add(Printer)
    return Printer

def _cant_register_printer(Printer):
    print >> sys.stderr, 'Printer [%s] not supported by this gdb version' % Printer.printer_name
    return Printer

def _conditionally_register_printer(condition):
    if condition:
        return _register_printer
    else:
        return _cant_register_printer

@_register_printer
class NfdNameTree:
    "Pretty Printer for nfd::NameTree"
    printer_name = 'nfd::NameTree'
    version = '0.4.1'

    @staticmethod
    def supports(v):
        return str(v.basic_type) == "nfd::NameTree"

    class Iterator:
        def __init__(self, pointer, capacity):
            self.pointer = pointer
            self.capacity = capacity
            self.bucket = 0

        def __iter__(self):
            return self

        def next(self):
            for i in range(self.bucket, self.capacity):
                if self.pointer[i] != 0:
                    break

            if self.bucket + 1 >= self.capacity:
                raise StopIteration

            elt = self.pointer[i]['m_entry']['_M_ptr'].dereference()

            self.bucket = i + 1
            return ('m_buckets[%d]' % (self.bucket - 1), elt)

    def __init__(self, value):
        self.val = value

    def get_pointer(self):
        return self.val["m_buckets"]

    def get_size(self):
        return self.val["m_nItems"]

    def get_capacity(self):
        return self.val["m_nBuckets"]

    def has_elements(self):
        if self.get_pointer():
            return True
        else:
            return False

    def to_string (self):
        if (self.has_elements()):
            return "nfd::NameTree with %d elements, buckets %d" % (
                self.get_size(), self.get_capacity())
        else:
            return "empty nfd::NameTree"

    def children(self):
        return self.Iterator(self.get_pointer(), self.get_capacity())

    # def display_hint(self):
    #     return "map"

@_register_printer
class NfdNameTreeEntry:
    "Pretty Printer for nfd::name_tree::Entry"
    printer_name = 'nfd::name_tree::Entry'
    version = '0.4.1'

    VectorOfPitEntries = None
    VectorOfNameTreeEntries = None

    @staticmethod
    def supports(v):
        return str(v.basic_type) == "nfd::name_tree::Entry"

    def __init__(self, value):
        self.val = value

    def to_string(self):

        if self.VectorOfPitEntries == None:
            xVector = gdb.xmethods[gdb.xmethod._lookup_xmethod_matcher(gdb, 'libstdc++::vector')]._method_dict['size'].worker_class
            self.VectorOfPitEntries = xVector(gdb.lookup_type("std::shared_ptr<nfd::pit::Entry>"))
            self.VectorOfNameTreeEntries = xVector(gdb.lookup_type("std::shared_ptr<nfd::name_tree::Entry>"))

        name = self.val['m_prefix']['m_nameBlock']
        nameValue = name['m_buffer']['_M_ptr'].dereference()['_M_impl']['_M_start']
        nameMem = gdb.selected_inferior().read_memory(nameValue, name['m_size'])

        name = pyndn.Name()
        name.wireDecode(pyndn.Blob.fromRawStr(nameMem))

        fib = self.val['m_fibEntry']['_M_ptr']
        p = self.val['m_pitEntries']
        m = self.val['m_measurementsEntry']['_M_ptr']
        s = self.val['m_strategyChoiceEntry']['_M_ptr']

        parent = self.val['m_parent']['_M_ptr']
        children = self.val['m_children']

        return '{"nFIB": %d, "nPIT": %d, "nMsmnts": %d, "nSC": %d, "nParent": %d, "nChildren": %d, "Prefix": "%s"},' % (fib != 0, self.VectorOfPitEntries.size(p), m != 0, s != 0,
                 parent != 0, self.VectorOfNameTreeEntries.size(children),
                 name.toUri())

@_register_printer
class NdnName:
    "Pretty Printer for ndn::Name"
    printer_name = 'ndn::Name'
    version = '0.4.1'

    @staticmethod
    def supports(v):
        return str(v.basic_type) == "ndn::Name"

    def __init__(self, value):
        self.value = value

    def to_string(self):
        name = self.value['m_nameBlock']
        if name['m_size'] == 0 or name['m_buffer']['_M_ptr'] == 0:
            return None

        try:
            nameBegin = name['m_begin']['_M_current']
            nameEnd = name['m_end']['_M_current']
            nameMem = gdb.selected_inferior().read_memory(nameBegin, nameEnd - nameBegin)

            nName = pyndn.Name()
            nName.wireDecode(pyndn.Blob.fromRawStr(nameMem))
            return nName.toUri()
        except ValueError:
            return "<ERROR>"

    def display_hint(self):
        return "string"

def dumpForwarder(obj):
    tree = NfdNameTree(gdb.parse_and_eval(obj + ".get()->m_nameTree"))

    print '{';

    pit = gdb.parse_and_eval(obj + ".get()->m_pit.m_nItems")
    fib = gdb.parse_and_eval(obj + ".get()->m_fib.m_nItems")
    ms = gdb.parse_and_eval(obj + ".get()->m_measurements.m_nItems")
    sc = gdb.parse_and_eval(obj + ".get()->m_strategyChoice.m_nItems")

    print '"PIT": {"size": %d},' % pit
    print '"FIB": {"size": %d},' % fib
    print '"Measurements": {"size": %d},' % ms
    print '"StrategyChoice": {"size": %d},' % sc

    print '"NameTree": {"size": %d, "items": [' % tree.get_size()

    for item in tree.children():
        print item[1]
    print '] } }'

# class NameTreeEntryPit(gdb.xmethod.XMethodWorker):
#     def get_arg_types(self):
#         return None

#     def __call__(self, obj):
#         return obj['_M_ptr']


# class NameTreeMatcher(gdb.xmethod.XMethodMatcher):
#     def __init__(self):
#         gdb.xmethod.XMethodMatcher.__init__(self, 'nfd::NameTree')
#         # self._get_worker = SharedPtrGetWorker()
#         # self._deref_worker = SharedPtrDerefWorker()
#         # self.methods = [self._get_worker, self._deref_worker]

#     def match(self, class_type, method_name):
#         if not re.match('^nfd::NameTree$', class_type.tag):
#             return None
#         if method_name == 'operator*' and self._deref_worker.enabled:
#             return self._deref_worker
#         elif method_name == 'get' and self._get_worker.enabled:
#             return self._get_worker

# def register_libstdcxx_xmethods(locus):
#     gdb.xmethod.register_xmethod_matcher(locus, ArrayMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(locus, ForwardListMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(locus, DequeMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(locus, ListMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(locus, VectorMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('set'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('map'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('multiset'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('multimap'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('unordered_set'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('unordered_map'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('unordered_multiset'))
#     gdb.xmethod.register_xmethod_matcher(
#         locus, AssociativeContainerMethodsMatcher('unordered_multimap'))
#     gdb.xmethod.register_xmethod_matcher(locus, UniquePtrMethodsMatcher())
#     gdb.xmethod.register_xmethod_matcher(locus, SharedPtrMethodsMatcher())
