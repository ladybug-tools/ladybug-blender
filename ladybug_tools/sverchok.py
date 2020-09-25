"""Functions for dealing with inputs and outputs from Grasshopper components."""
import collections

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
    Pattern = collections.namedtuple('Pattern', 'path list')

    for i, path in enumerate(input.Paths):
        data = input.Branch(path)
        branch = Pattern(path, [])

        for d in data:
            if d is not None:
                branch.list.append(d)

        all_data[i] = branch

    return all_data


def list_to_data_tree(input, root_count=0):
    """Transforms nested of lists or tuples to a Grasshopper DataTree"""
    return input

    def proc(input, tree, track):
        for i, item in enumerate(input):
            if isinstance(item, (list, tuple)):  # don't count iterables like colors
                track.append(i)
                proc(item, tree, track)
                track.pop()
            else:
                tree.Add(item, Path(*track))

    if input is not None:
        t = DataTree[object]()
        proc(input, t, [root_count])
        return t


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
