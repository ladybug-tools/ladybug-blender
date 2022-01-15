"""Functions for dealing with inputs and outputs from Grasshopper components."""
import collections
import multiprocessing
import types

# Stub for .net tasks.

def for_each(iterable, fn):
    for i in iterable:
        fn(i)
    return # Does this work in Sverchok?

    pool = multiprocessing.Pool()
    pool.map(fn, iterable)
    pool.close()
    pool.join()

tasks = types.SimpleNamespace()
Parallel = types.SimpleNamespace()
Parallel.ForEach = for_each
tasks.Parallel = Parallel


def give_warning(component, message):
    """Give a warning message (turning the component orange).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        message: Text string for the warning message.
    """
    return "TODO"
    component.AddRuntimeMessage(Message.Warning, message)


def give_remark(component, message):
    """Give an remark message (giving a little grey ballon in the upper left).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        message: Text string for the warning message.
    """
    return "TODO"
    component.AddRuntimeMessage(Message.Remark, message)


def give_popup_message(message, window_title='', icon_type='information'):
    """Give a Windows popup message with an OK button.

    Useful in cases where you really need the user to pay attention to the message.

    Args:
        message: Text string for the popup message.
        window_title: Text string for the title of the popup window. (Default: "").
        icon_type: Text for the type of icon to be used. (Default: "information").
            Choose from the following options.

            * information
            * warning
            * error

    """
    print(icon_type, window_title, message)
    return "TODO"
    icon_types = {
        'information': Forms.MessageBoxIcon.Information,
        'warning': Forms.MessageBoxIcon.Warning,
        'error': Forms.MessageBoxIcon.Error
    }
    icon = icon_types[icon_type]
    buttons = Forms.MessageBoxButtons.OK
    rui.Dialogs.ShowMessageBox(message, window_title, buttons, icon)


def all_required_inputs(component):
    """Check that all required inputs on a component are present.

    Note that this method needs required inputs to be written in the correct
    format on the component in order to work (required inputs have a
    single _ at the start and no _ at the end).

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.

    Returns:
        True if all required inputs are present. False if they are not.
    """
    return "TODO"
    is_input_missing = False
    for param in component.Params.Input:
        if param.NickName.startswith('_') and not param.NickName.endswith('_'):
            missing = False
            if not param.VolatileDataCount:
                missing = True
            elif param.VolatileData[0][0] is None:
                missing = True

            if missing is True:
                msg = 'Input parameter {} failed to collect data!'.format(param.NickName)
                print(msg)
                give_warning(component, msg)
                is_input_missing = True
    return not is_input_missing


def local_processor_count():
    """Get an integer for the number of processors on this machine.

    If, for whatever reason, the number of processors could not be sensed,
    None will be returned.
    """
    return multiprocessing.cpu_count()


def recommended_processor_count():
    """Get an integer for the recommended number of processors for parallel calculation.

    This should be one less than the number of processors available on this machine
    unless the machine has only one processor, in which case 1 will be returned.
    If, for whatever reason, the number of processors could not be sensed, a value
    of 1 will be returned.
    """
    cpu_count = local_processor_count()
    return 1 if cpu_count is None or cpu_count <= 1 else cpu_count - 1


def run_function_in_parallel(parallel_function, object_count, cpu_count=None):
    """Run any function in parallel given a number of objects to be iterated over.

    This method can run the calculation in a manner that targets a given CPU
    count and will also run the function normally (without the use of Tasks)
    if only one CPU is specified.

    Args:
        parallel_function: A function which will be iterated over in a parallelized
            manner. This function should have a single input argument, which
            is the integer of the object to be simulated. Note that, in order
            for this function to be successfully parallelized, any lists of
            output data must be set up beforehand and this parallel_function
            should simply be replacing the data in this pre-created list.
        object_count: An integer for the number of objects which will be iterated over
            in a parallelized manner.
        cpu_count: An integer for the number of CPUs to be used in the intersection
            calculation. The ladybug_rhino.grasshopper.recommended_processor_count
            function can be used to get a recommendation. If set to None, all
            available processors will be used. (Default: None).
    """

    def compute_each_object_group(worker_i):
        """Run groups of objects so that only the cpu_count is used."""
        start_i, stop_i = obj_groups[worker_i]
        for count in range(start_i, stop_i):
            parallel_function(count)

    if cpu_count is not None and cpu_count > 1:
        # group the objects in order to meet the cpu_count
        worker_count = min((cpu_count, object_count))
        i_per_group = int(math.ceil(object_count / worker_count))
        obj_groups = [[x, x + i_per_group] for x in range(0, object_count, i_per_group)]
        obj_groups[-1][-1] = object_count  # ensure the last group ends with obj count

    if cpu_count is None:  # use all availabe CPUs
        tasks.Parallel.ForEach(range(object_count), parallel_function)
    elif cpu_count <= 1:  # run everything on a single processor
        for i in range(object_count):
            parallel_function(i)
    else:  # run the groups in a manner that meets the CPU count
        tasks.Parallel.ForEach(range(len(obj_groups)), compute_each_object_group)


def component_guid(component):
    """Get the unique ID associated with a specific component.

    This ID remains the same every time that the component is run.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.

    Returns:
        Text string for the component's unique ID.
    """
    return "TODO"
    return component.GetHashCode().ToString()


def bring_to_front(component):
    """Bring a component to the front of the canvas so that it is always executed last.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
    """
    return "TODO"
    doc = Instances.ActiveCanvas.Document.Objects
    in_front = doc[doc.Count - 1].InstanceGuid.Equals(component.InstanceGuid)
    if not in_front:  # bring the component to the top
        component.OnPingDocument().DeselectAll()  # de-select all components
        component.Attributes.Selected = True  # select the component to move
        component.OnPingDocument().BringSelectionToTop()
        component.Attributes.Selected = False  # de-select the component after moving


def send_to_back(component):
    """Send a component to the back of the canvas so that it is always executed first.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
    """
    return "TODO"
    doc = Instances.ActiveCanvas.Document.Objects
    in_back = doc[0].InstanceGuid.Equals(component.InstanceGuid)
    if not in_back:  # send the component to the back
        component.OnPingDocument().SelectAll()  # select all components
        component.Attributes.Selected = False  # de-select the component to move
        component.OnPingDocument().BringSelectionToTop()
        component.OnPingDocument().DeselectAll()  # de-select all after moving


def wrap_output(output):
    """Wrap Python objects as Grasshopper generic objects.

    Passing output lists of Python objects through this function can greatly reduce
    the time needed to run the component since Grasshopper can spend a long time
    figuring out the object type is if it is not recognized.  However, if the number
    of output objects is usually < 100, running this method won't make a significant
    difference and so there's no need to use it.

    Args:
        output: A list of values to be wrapped as a generic Grasshopper Object (GOO).
    """
    return output
    if not output:
        return output
    try:
        return (Goo(i) for i in output)
    except Exception as e:
        raise ValueError('Failed to wrap {}:\n{}.'.format(output, e))


def objectify_output(object_name, output_data):
    """Wrap data into a single custom Python object that can later be de-serialized.

    This is meant to address the same issue as the wrap_output method but it does
    so by simply hiding the individual items from the Grasshopper UI within a custom
    parent object that other components can accept as input and de-objectify to
    get access to the data. This strategy is also useful for the case of standard
    object types like integers where the large number of data points slows down
    the Grasshopper UI when they are output.

    Args:
        object_name: Text for the name of the custom object that will wrap the data.
            This is how the object will display in the Grasshopper UI.
        output_data: A list of data to be stored under the data property of
            the output object.
    """
    class Objectifier(object):
        """Generic class for objectifying data."""

        def __init__(self, name, data):
            self.name = name
            self.data = data

        def ToString(self):
            return '{} ({} items)'.format(self.name, len(self.data))

    return Objectifier(object_name, output_data)


def de_objectify_output(objectified_data):
    """Extract the data from an object that was output from the objectify_output method.

    Args:
        objectified_data: An object that has been output from the objectify_output
            method for which data will be returned.
    """
    return objectified_data.data


def document_counter(counter_name):
    """Get an integer for a counter name that advances each time this function is called.

    Args:
        counter_name: The name of the counter that will be advanced.
    """
    return "TODO"
    try:  # get the counter and advance it one value
        scriptcontext.sticky[counter_name] += 1
    except KeyError:  # first time that the counter is called
        scriptcontext.sticky[counter_name] = 1
    return scriptcontext.sticky[counter_name]


def longest_list(values, index):
    """Get a value from a list while applying Grasshopper's longest-list logic.

    Args:
        values: An array of values from which a value will be pulled following
            longest list logic.
        index: Integer for the index of the item in the list to return. If this
            index is greater than the length of the values, the last item of the
            list will be returned.
    """
    try:
        return values[index]
    except IndexError:
        return values[-1]


def data_tree_to_list(input):
    """Convert a grasshopper DataTree to nested lists of lists.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        listData -- A list of namedtuples (path, dataList)
    """
    return input
    all_data = list(range(len(input.Paths)))
    pattern = collections.namedtuple('Pattern', 'path list')

    for i, path in enumerate(input.Paths):
        data = input.Branch(path)
        branch = pattern(path, [])

        for d in data:
            if d is not None:
                branch.list.append(d)

        all_data[i] = branch

    return all_data


def list_to_data_tree(input, root_count=0, s_type=object):
    """Transform nested of lists or tuples to a Grasshopper DataTree.

    Args:
        input: A nested list of lists to be converted into a data tree.
        root_count: An integer for the starting path of the data tree.
        s_type: An optional data type (eg. float, int, str) that defines all of the
            data in the data tree. The default (object) works will all data types
            but the conversion to data trees can be more efficient if a more
            specific type is specified.
    """
    return input

    def proc(input, tree, track):
        for i, item in enumerate(input):
            if isinstance(item, (list, tuple, array.array)):  # ignore iterables like str
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                tree.Add(item, Path(*track))

    if input is not None:
        t = DataTree[s_type]()
        proc(input, t, [root_count])
        return t


def merge_data_tree(data_trees, s_type=object):
    """Merge a list of grasshopper DataTrees into a single DataTree.

    Args:
        input: A list Grasshopper DataTrees to be merged into one.
        s_type: An optional data type (eg. float, int, str) that defines all of the
            data in the data tree. The default (object) works will all data types
            but the conversion to data trees can be more efficient if a more
            specific type is specified.
    """
    return data_trees
    comb_tree = DataTree[s_type]()
    for d_tree in data_trees:
        for p, branch in zip(d_tree.Paths, d_tree.Branches):
            comb_tree.AddRange(branch, p)
    return comb_tree


def flatten_data_tree(input):
    """Flatten and clean a grasshopper DataTree into a single list and a pattern.

    Args:
        input: A Grasshopper DataTree.

    Returns:
        A tuple with two elements

        -   all_data -- All data in DataTree as a flattened list.

        -   pattern -- A dictionary of patterns as namedtuple(path, index of last item
            on this path, path Count). Pattern is useful to un-flatten the list
            back to a DataTree.
    """
    return input
    Pattern = collections.namedtuple('Pattern', 'path index count')
    pattern = dict()
    all_data = []
    index = 0  # Global counter for all the data
    for i, path in enumerate(input.Paths):
        count = 0
        data = input.Branch(path)

        for d in data:
            if d is not None:
                count += 1
                index += 1
                all_data.append(d)

        pattern[i] = Pattern(path, index, count)

    return all_data, pattern


def unflatten_to_data_tree(all_data, pattern):
    """Create DataTree from a single flattened list and a pattern.

    Args:
        all_data: A flattened list of all data
        pattern: A dictionary of patterns
            Pattern = namedtuple('Pattern', 'path index count')

    Returns:
        data_tree -- A Grasshopper DataTree.
    """
    return all_data
    data_tree = DataTree[Object]()
    for branch in range(len(pattern)):
        path, index, count = pattern[branch]
        data_tree.AddRange(all_data[index - count:index], path)

    return data_tree


def recipe_result(result):
    """Process a recipe result and handle the case that it's a list of list.

    Args:
        result: A recipe result to be processed.
    """
    if isinstance(result, (list, tuple)):
        return list_to_data_tree(result)
    return result


def hide_output(component, output_index):
    """Hide one of the outputs of a component.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        output_index: Integer for the index of the output to hide.
    """
    return "TODO"
    component.Params.Output[output_index].Hidden = True


def show_output(component, output_index):
    """Show one of the outputs of a component.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        output_index: Integer for the index of the output to hide.
    """
    return
    component.Params.Output[output_index].Hidden = False


def schedule_solution(component, milliseconds):
    """Schedule a new Grasshopper solution after a specified time interval.

    Args:
        component: The grasshopper component object, which can be accessed through
            the ghenv.Component call within Grasshopper API.
        milliseconds: Integer for the number of milliseconds after which the
            solution should happen.
    """
    return
    doc = component.OnPingDocument()
    doc.ScheduleSolution(milliseconds)
